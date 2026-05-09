"""Hybrid (regex + LLM) fault-code pattern detector.

Strategy
--------
Fault-list locating and code extraction are split into two stages with
different reliability profiles:

1.  **TOC-regex fault-page locator** (no LLM). Scans the first ~40 pages
    for TOC lines that mention "fault/alarm/error list" with a trailing
    page number. Works for Yaskawa, Fanuc, Mitsubishi, Schneider out of
    the box. Cheap, deterministic, fails clean.

2.  **LLM regex inference** (used only when stage 1 found pages). Sends
    the actual fault-list page text to the LLM and asks it to infer the
    code format(s). Output is validated: every example must match a
    returned regex, otherwise we throw the LLM result away.

3.  **Whitelist build**: apply validated regexes to the located fault
    pages → extract every match → dedupe = whitelist.

If any stage fails, return None and let the caller fall back to
`chunking_v2._extract_error_codes` (legacy regex). No silent-bad output.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path

import fitz  # PyMuPDF
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import get_settings
from app.core.llm import get_llm

logger = logging.getLogger(__name__)

_NO_THINK = SystemMessage(content="/no_think")
_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)

# TOC scoring — rank lines by how strongly they suggest a fault-list section
_STRONG_TOC_RE = re.compile(
    r"\b(?:list|table|index)\b.*?\b(?:fault|alarm|error|trouble[- ]?shoot)\w*\b",
    re.IGNORECASE,
)
_ALSO_TOC_RE = re.compile(
    r"\b(?:fault|alarm|error|trouble[- ]?shoot)\w*\b.*?"
    r"\b(?:list|table|codes?|messages?|detection|group)\b",
    re.IGNORECASE,
)
_NEGATIVE_TOC_RE = re.compile(
    r"\b(?:ground\s+fault|fault\s+reset|fault\s+monitoring|"
    r"safety|filing|reporting|message\s+can|warnings?\s+and|caution)\b",
    re.IGNORECASE,
)
_TRAIL_PAGE_RE = re.compile(r"(\d{1,4})\s*$")
_TOC_SCAN_PAGES = 40
_MAX_FAULT_PAGE_SPAN = 80  # cap how far we extend a single fault list

# Safety net for prose noise the LLM regex might accept
_BLACKLIST_TOKENS = {
    "RS-485", "RS-232", "RS-422", "RJ-45", "USB-2", "USB-3",
    "EN-61800", "IEC-61800", "IEC-62061", "ISO-13849",
}

# Common English short words that pollute mnemonic-style fault whitelists
# (e.g. Yaskawa-style 2-3 letter codes accidentally also match prose tokens
# like "AND", "AS", "OF"). Lowercase here; comparison is case-insensitive.
_ENGLISH_STOPWORDS = {
    # 1-letter
    "a", "i",
    # 2-letter
    "an", "as", "at", "be", "by", "do", "go", "he", "if", "in", "is", "it",
    "me", "my", "no", "of", "on", "or", "so", "to", "up", "us", "we",
    "ms", "kw", "kg", "hz", "ip", "us", "uk", "id", "ok", "tv", "pc",
    # 3-letter
    "all", "and", "any", "are", "but", "can", "did", "for", "get", "had",
    "has", "her", "him", "his", "how", "its", "let", "may", "new", "not",
    "now", "off", "old", "one", "our", "out", "own", "see", "set", "she",
    "the", "too", "two", "use", "was", "way", "who", "you", "yes", "via",
    "min", "max", "low", "old", "via", "non", "yet", "amp", "bad", "big",
    # 4+ letter common words you sometimes see in tables
    "able", "auto", "back", "case", "code", "data", "date", "down", "each",
    "edit", "even", "from", "good", "have", "here", "high", "into", "just",
    "last", "left", "like", "list", "look", "made", "main", "make", "many",
    "more", "most", "much", "must", "name", "next", "none", "note", "only",
    "open", "over", "page", "part", "rate", "read", "ring", "same", "send",
    "show", "size", "some", "such", "sure", "take", "test", "text", "than",
    "that", "them", "then", "they", "this", "time", "type", "used", "user",
    "very", "view", "want", "warn", "what", "when", "with", "your", "zero",
    "stop", "step", "long", "load", "tool", "byte", "bits", "mode", "high",
    "good", "fast", "slow", "true", "wait", "work", "year", "save", "seek",
    "free", "full", "half", "hold", "hour", "hours", "lock",
    "able", "save",
}


def _looks_like_english_word(tok: str) -> bool:
    return tok.lower() in _ENGLISH_STOPWORDS


@dataclass(frozen=True)
class FaultRow:
    """One row of a vendor fault-list table — the unit a user query targets."""
    code: str
    page: int
    text: str  # joined cell text (code + name + description + remedy ...)

    def as_dict(self) -> dict:
        return {"code": self.code, "page": self.page, "text": self.text}


@dataclass(frozen=True)
class FaultPattern:
    manual_id: str
    vendor_hint: str | None
    fault_pages: tuple[int, int] | None
    regexes: tuple[str, ...] = ()
    examples: tuple[str, ...] = ()
    whitelist: tuple[str, ...] = ()
    rows: tuple[FaultRow, ...] = ()  # populated when source == "toc+tables"
    source: str = "none"  # "toc+tables" | "toc+llm" | "toc-only" | "none"

    def as_dict(self) -> dict:
        return {
            "manual_id": self.manual_id,
            "vendor_hint": self.vendor_hint,
            "fault_pages": list(self.fault_pages) if self.fault_pages else None,
            "regexes": list(self.regexes),
            "examples": list(self.examples),
            "whitelist": list(self.whitelist),
            "rows": [r.as_dict() for r in self.rows],
            "source": self.source,
        }


# ---------- Step 1: TOC-regex fault-page locator ----------


def _locate_fault_pages_via_toc(doc: fitz.Document) -> list[tuple[int, int, str]]:
    """Return [(referenced_page, score, line_text)] for plausible fault entries.

    We don't pick a single range here — we hand back all candidates so
    `_select_fault_range` can cluster them.
    """
    out: list[tuple[int, int, str]] = []
    for pno in range(min(_TOC_SCAN_PAGES, doc.page_count)):
        text = doc[pno].get_text("text")
        for line in text.splitlines():
            ln = line.strip()
            if not ln or len(ln) > 220:
                continue
            if _NEGATIVE_TOC_RE.search(ln):
                continue
            score = (
                3 if _STRONG_TOC_RE.search(ln)
                else 1 if _ALSO_TOC_RE.search(ln)
                else 0
            )
            if score == 0:
                continue
            tp = _TRAIL_PAGE_RE.search(ln)
            if not tp:
                continue
            ref_page = int(tp.group(1))
            if ref_page <= pno + 1:
                # trailing number must point at a later page
                continue
            out.append((ref_page, score, ln))
    return out


def _select_fault_range(
    candidates: list[tuple[int, int, str]],
    page_count: int,
) -> tuple[int, int] | None:
    """Pick a [start, end] range from clustered TOC candidates.

    Heuristic:
      - take the highest-scoring candidate as the seed
      - merge any other candidate within ±span_limit pages
      - end = max(referenced_page) + small slack, capped at page_count
    """
    if not candidates:
        return None
    candidates.sort(key=lambda c: (-c[1], c[0]))
    seed = candidates[0]
    seed_page = seed[0]
    cluster = [c[0] for c in candidates if abs(c[0] - seed_page) <= _MAX_FAULT_PAGE_SPAN]
    if not cluster:
        cluster = [seed_page]
    start = min(cluster)
    end = min(page_count, max(cluster) + 30)  # 30p slack past last TOC entry
    if end - start > _MAX_FAULT_PAGE_SPAN:
        end = start + _MAX_FAULT_PAGE_SPAN
    return start, end


# ---------- Step 1.5: PyMuPDF table-extraction shortcut ----------


_CODE_CELL_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._\-]{1,18}$")


def _looks_like_code_cell(cell: str | None) -> str | None:
    """Return the cleaned token if `cell` plausibly contains exactly one
    fault code as its leading token, else None.

    Vendor fault tables put the code in the first cell. The cell may be:
      - clean code: "F040", "SOF", "oFA10"
      - code with hex address: "dWA2 (004A)", "AEr (0032)"
      - multi-code (rare): "EF1\nEF2" — take the first.
    """
    if not cell:
        return None
    raw = cell.strip()
    if not raw:
        return None
    # split off `(hex)` and any newline continuation
    head = raw.split("\n", 1)[0].strip()
    head = head.split("(", 1)[0].strip()
    if not head:
        return None
    if _looks_like_english_word(head):
        return None
    if not _CODE_CELL_RE.match(head):
        return None
    if head.upper() in {"NO", "NAME", "TYPE", "REF", "CODE", "ITEM", "DESC"}:
        return None
    return head


_FAULT_HEADER_RE = re.compile(
    r"\b(?:fault|alarm|error|code|display|no\.?|number|alm|symptom)\b",
    re.IGNORECASE,
)


def _table_first_column_codes(
    doc: fitz.Document, fault_pages: tuple[int, int]
) -> tuple[list[str], list[FaultRow]]:
    """Sweep the fault pages with PyMuPDF table detection and harvest the
    first column of each detected table.

    Returns (codes, rows) where:
      - `codes` is the deduped first-column code list (whitelist material).
      - `rows` is the per-(code, page) row payload — the joined cell text
        of every row whose first column matched. The caller (ingest) turns
        each row into a "table" Section so retrieval can hit `code` and
        the LLM still sees the row's name/cause/remedy text.

    Filtering layers:
      - Skip tables whose header row's first cell is a non-fault label
        (e.g. an accessory parts table like "Item / Description / Catalog").
      - Per-cell, only accept short alnum tokens that don't look like
        English words (`_looks_like_code_cell`).
      - First (code, page) wins — duplicate occurrences ignored.
    """
    start, end = fault_pages
    start = max(1, start)
    end = min(doc.page_count, end)
    codes_order: dict[str, None] = {}
    rows_by_code: dict[str, FaultRow] = {}
    for pno in range(start - 1, end):
        try:
            tabs = doc[pno].find_tables()
        except Exception as exc:  # noqa: BLE001 — find_tables can throw on weird layouts
            logger.debug("find_tables failed on p%d: %s", pno + 1, exc)
            continue
        for t in tabs.tables:
            try:
                table_rows = t.extract()
            except Exception:
                continue
            if not table_rows or len(table_rows) < 2:
                continue
            header_first = (table_rows[0][0] or "").strip() if table_rows[0] else ""
            if header_first and not _FAULT_HEADER_RE.search(header_first):
                continue
            for row in table_rows[1:]:
                if not row:
                    continue
                code = _looks_like_code_cell(row[0])
                if not code:
                    continue
                joined = "\n".join(c.strip() for c in row if c and c.strip())
                # A real fault row carries a description, not just "<code> <page>".
                # Index/cross-reference tables look like ("LFr1", "59") — the
                # second cell is a page number and there's no remedy text.
                # Reject rows shorter than 25 chars or whose only non-code
                # tokens are pure digits.
                non_code = joined.replace(code, "", 1).strip()
                if len(joined) < 25:
                    continue
                # all-digit second column → cross-reference table, drop
                tokens = [t for t in re.split(r"\s+", non_code) if t]
                if tokens and all(t.isdigit() for t in tokens):
                    continue
                codes_order[code] = None
                if code in rows_by_code:
                    continue
                rows_by_code[code] = FaultRow(code=code, page=pno + 1, text=joined)
    return list(codes_order.keys()), list(rows_by_code.values())


# ---------- Step 2: LLM regex inference (JSON-mode Ollama / OpenAI) ----------


def _build_detector_llm():
    settings = get_settings()
    if settings.llm_provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=0.0,
            format="json",
        )
    if settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI

        if not settings.openai_api_key:
            raise RuntimeError("LLM_PROVIDER=openai but OPENAI_API_KEY is not set.")
        return ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=0.0,
            model_kwargs={"response_format": {"type": "json_object"}},
        )
    return get_llm(settings)


def _safe_json(raw: str) -> dict | None:
    raw = (raw or "").strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].lstrip()
    m = _JSON_BLOCK_RE.search(raw)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


_REGEX_PROMPT = """\
You are reading the FAULT / ALARM / ERROR CODE LIST pages of a drive /
controller / robot manual. Your only job: identify the FORMAT of the
fault codes that the operator sees on the device display when an error
occurs.

A fault code is the short identifier printed in the FIRST column of the
fault table — the thing the user types in support tickets, e.g.:
  ABB:        "40747", "111851"
  Yaskawa:    "bb", "bUS", "oFA10", "oPE10", "EF3", "Err"
  Rockwell:   "F003", "F040", "F708", "A001"
  Schneider:  "OCF", "SOF", "CrF", "InF1", "USF"
  Mitsubishi: "AL.30", "[AL.50]", "AL.E4", "67.1"
  Fanuc:      "1820", "1850", "E-0200"

The following are NOT fault codes — never include them:
  - Page numbers ("417", "- 332 -", "p.46")
  - Section / chapter headings ("11.2.3", "1.4", "A.2", "Section 6.3")
  - Document IDs ("B-64305EN/03", "NVE41295", "3HAC020738-001")
  - Cable / protocol names ("RS-485", "RJ-45", "USB-2.0")
  - Industry standards ("IEC 61800-5-2", "EN 62061")
  - Catalog / part numbers ("25-MAP-FA", "RTEN-5006", "MR-J4-DU")
  - Hexadecimal Modbus addresses shown in parentheses ("(0008)", "(0085)")
    These appear next to a real code and are NOT the code itself.
  - Model names ("S7-1500", "GA700", "PowerFlex 520", "ATV320")

Output ONLY a JSON object with these keys (exactly):
  {{
    "regexes": ["<python regex 1>", ...],
    "examples": ["<exact code 1>", "<exact code 2>", ..., "<at least 5>"]
  }}

Strict rules:
- Every regex must match at least one of your examples.
- Examples are the EXACT operator-facing code strings, no surrounding
  punctuation or descriptions.
- If the vendor uses two distinct formats (e.g. mnemonic codes "bUS" plus
  numeric codes "0015"), emit ONE regex per format AND keep examples for
  each.
- Anchor regexes with `\\b` or character-class boundaries so they don't
  match prose words.
- Aim for the MNEMONIC / DISPLAY code, not the parenthesised hex address.

Sample lines from the fault/alarm pages of THIS manual:
{sample}
"""


_FOOTER_NOISE_RE = re.compile(
    r"^\s*(?:-?\s*\d{1,4}\s*-?\s*$|p?age\s*\d+|©.*|"
    r"YASKAWA.*|Rockwell.*|NVE\d+|B-\d{5}|3HAC\d+|MR-J4|"
    r"\w*\.\d+(?:\.\d+)*\s*$)",
    re.IGNORECASE,
)


def _filter_page_lines(text: str) -> str:
    """Drop running headers/footers and obvious noise lines from a page."""
    out: list[str] = []
    for line in text.splitlines():
        ln = line.rstrip()
        if not ln.strip():
            continue
        if _FOOTER_NOISE_RE.match(ln.strip()):
            continue
        # drop lone all-digit lines (page numbers)
        if ln.strip().isdigit() and len(ln.strip()) <= 4:
            continue
        out.append(ln)
    return "\n".join(out)


def _sample_fault_pages(
    doc: fitz.Document, fault_pages: tuple[int, int], max_chars: int = 8000
) -> str:
    start, end = fault_pages
    start = max(1, start)
    end = min(doc.page_count, end)
    parts: list[str] = []
    total = 0
    for pno in range(start - 1, end):
        text = _filter_page_lines(doc[pno].get_text("text"))
        if not text:
            continue
        block = f"--- p{pno + 1} ---\n{text}"
        if total + len(block) > max_chars:
            parts.append(block[: max_chars - total])
            break
        parts.append(block)
        total += len(block)
    return "\n".join(parts)


def _llm_infer_regexes(
    llm, doc: fitz.Document, fault_pages: tuple[int, int]
) -> tuple[list[str], list[str]]:
    sample = _sample_fault_pages(doc, fault_pages)
    if not sample:
        return [], []
    prompt = _REGEX_PROMPT.format(sample=sample)
    raw = llm.invoke(
        [_NO_THINK, HumanMessage(content=f"/no_think\n\n{prompt}")]
    ).content
    parsed = _safe_json(raw)
    if not parsed:
        logger.warning("regex JSON parse failed — raw=%r", (raw or "")[:200])
        return [], []
    regexes = parsed.get("regexes") or []
    examples = parsed.get("examples") or []
    if not isinstance(regexes, list) or not isinstance(examples, list):
        return [], []
    regexes = [_repair_regex(r) for r in regexes if isinstance(r, str) and r.strip()]
    examples = [e.strip() for e in examples if isinstance(e, str) and e.strip()]
    return regexes, examples


def _repair_regex(r: str) -> str:
    """Undo JSON-decoded backspace control chars that look like regex `\\b`.

    LLMs frequently write `\\b` in their text reasoning. JSON parsers
    interpret `"\\b"` as the backspace character (\\x08), so by the time
    we get the string the regex anchor is gone. Restore it. Same trick
    for `\\f` (form-feed -> regex `\\f` is rare and unused, skip).
    """
    return r.replace("\x08", r"\b").strip()


# ---------- Step 3: validate + build whitelist ----------


def _compile_safe(patterns):
    out = []
    for p in patterns:
        try:
            out.append(re.compile(p))
        except re.error as exc:
            logger.warning("invalid regex from LLM: %r (%s)", p, exc)
    return out


def _synthesize_regex_from_examples(examples: list[str]) -> list[str]:
    """Build a small set of conservative regexes that cover the LLM examples.

    Strategy: cluster examples by their abstract shape (uppercase / lowercase
    / digit / punct), then emit one anchored alternation per cluster. This is
    more reliable than asking qwen to write valid regex syntax.

    Example: ["F604", "F605", "F708"] -> shape `Addd` -> `\\bF\\d{3}\\b`.
    """
    if not examples:
        return []

    clusters: dict[str, list[str]] = {}
    for ex in examples:
        clusters.setdefault(_shape_of(ex), []).append(ex)

    out: list[str] = []
    for shp, members in clusters.items():
        # Build a regex from the shape pattern.
        parts: list[str] = []
        # collapse runs of the same kind (e.g. "UU" -> "[A-Z]{2}")
        run_kind = None
        run_len = 0
        flush = False

        def emit(kind: str | None, length: int):
            if kind == "U":
                parts.append(r"[A-Z]" + (f"{{{length}}}" if length > 1 else ""))
            elif kind == "L":
                parts.append(r"[a-z]" + (f"{{{length}}}" if length > 1 else ""))
            elif kind == "D":
                parts.append(r"\d" + (f"{{{length}}}" if length > 1 else ""))
            else:
                # literal: kind is the literal char
                parts.append(re.escape(kind * length))

        for ch in shp:
            cur = ch if ch in {"U", "L", "D"} else ch
            if cur == run_kind:
                run_len += 1
            else:
                if run_kind is not None:
                    emit(run_kind, run_len)
                run_kind = cur
                run_len = 1
        if run_kind is not None:
            emit(run_kind, run_len)
        body = "".join(parts)
        # Anchor: word boundary if the regex starts/ends with an alnum class,
        # else use a less aggressive boundary so it works on dotted shapes.
        out.append(rf"\b{body}\b")

    # Always include literal alternation as a fallback safety net so the
    # exact examples are guaranteed extractable even if shapes miss something
    # (e.g. mixed-case mnemonics where heuristic shape diverges).
    literal = r"\b(?:" + "|".join(re.escape(e) for e in examples) + r")\b"
    out.append(literal)
    return out


def _validate_examples(examples: list[str], min_count: int = 5) -> bool:
    """Sanity: examples must look like fault codes, not prose / generic terms.

    Reject the whole detection if too many examples are obvious noise —
    English words, generic "WARNING/NOTE", phrases, brackets.
    """
    if len(examples) < min_count:
        return False
    bad = 0
    for ex in examples:
        if " " in ex or len(ex) > 20 or len(ex) < 2:
            bad += 1
            continue
        # single-letter mnemonics are almost never real fault codes
        if len(ex) < 2:
            bad += 1
            continue
        if ex.startswith("[") and ex.endswith("]"):
            bad += 1
            continue
        if ex.upper() in {"NOTE", "WARNING", "CAUTION", "ACTION", "REMEDY",
                          "EXPLANATION", "DESCRIPTION", "TYPE", "REF", "NAME"}:
            bad += 1
            continue
        if _looks_like_english_word(ex):
            bad += 1
            continue
        if ex.isdigit() and len(ex) < 3:
            bad += 1
    return bad <= len(examples) // 3


def _build_whitelist(
    doc: fitz.Document,
    fault_pages: tuple[int, int],
    regexes: list[str],
    examples: list[str],
) -> tuple[list[str], list[str]]:
    """Return (whitelist, regexes_used). Synthesises regexes from examples
    when the LLM-supplied ones are inconsistent with the examples.
    """
    if not _validate_examples(examples):
        logger.warning("LLM examples failed validation: %r", examples[:8])
        return [], regexes

    llm_compiled = _compile_safe(regexes)
    matched_by_llm = [
        ex for ex in examples if any(p.search(ex) for p in llm_compiled)
    ]
    threshold = max(3, len(examples) // 2)
    if llm_compiled and len(matched_by_llm) >= threshold:
        active_regexes = regexes
        active_compiled = llm_compiled
    else:
        # LLM regex unreliable — synthesise from examples.
        synthesised = _synthesize_regex_from_examples(examples)
        active_compiled = _compile_safe(synthesised)
        if not active_compiled:
            return [], regexes
        active_regexes = synthesised
        logger.info(
            "LLM regex matched only %d/%d examples — using synthesised regexes from examples",
            len(matched_by_llm), len(examples),
        )

    # Compute the SHAPE set of the LLM examples — a whitelist token only
    # passes if its shape matches one of the example shapes. This stops
    # generic 2-3 letter abbreviations (PCB, DRY, RAM) from sneaking in
    # under a permissive `\b[A-Z]{2,3}\b`-style synthesised regex.
    example_shapes = {_shape_of(e) for e in examples}

    # Minimum operator-facing-code length: 3 characters. 2-letter mnemonics
    # collide with English words and prose abbreviations so heavily that any
    # real signal is overwhelmed.
    min_len = 3

    sample = _sample_fault_pages(doc, fault_pages, max_chars=300_000)
    found: set[str] = {
        e for e in examples
        if _shape_of(e) in example_shapes
        and len(e) >= min_len
        and not _looks_like_english_word(e)
    }
    for p in active_compiled:
        for m in p.finditer(sample):
            tok = m.group(0).strip()
            if not (min_len <= len(tok) <= 40):
                continue
            if tok in _BLACKLIST_TOKENS:
                continue
            if _looks_like_english_word(tok):
                continue
            if _shape_of(tok) not in example_shapes:
                continue
            found.add(tok)

    # Sanity: if the whitelist exploded relative to examples, distrust it.
    # A real fault list rarely has more than ~30x the example count, but
    # accidental matches on prose words give 100s. Drop tokens that look
    # uniformly uppercase short (likely generic abbreviations).
    if len(found) > 60 * max(len(examples), 1):
        logger.warning(
            "whitelist size %d disproportionate to examples %d — distrusting",
            len(found), len(examples),
        )
        return [], regexes

    found = {t for t in found if not _looks_like_english_word(t)}
    return sorted(found), active_regexes


def _shape_of(s: str) -> str:
    """Same shape function as the synthesiser — uppercase letters become 'U',
    lowercase 'L', digits 'D', other characters keep themselves literally.
    """
    out = []
    for c in s:
        if c.isupper():
            out.append("U")
        elif c.islower():
            out.append("L")
        elif c.isdigit():
            out.append("D")
        else:
            out.append(c)
    return "".join(out)


# ---------- Public ----------


def detect_fault_pattern(
    pdf_path: str | Path,
    manual_id: str,
    *,
    llm=None,
    cache_dir: Path | None = None,
) -> FaultPattern | None:
    pdf_path = Path(pdf_path)

    if cache_dir is not None:
        cache_path = cache_dir / f"{manual_id}.fault_pattern.json"
        if cache_path.exists():
            try:
                data = json.loads(cache_path.read_text(encoding="utf-8"))
                fp = tuple(data["fault_pages"]) if data.get("fault_pages") else None
                rows = tuple(
                    FaultRow(
                        code=r["code"],
                        page=int(r["page"]),
                        text=r.get("text") or "",
                    )
                    for r in (data.get("rows") or [])
                )
                return FaultPattern(
                    manual_id=data["manual_id"],
                    vendor_hint=data.get("vendor_hint"),
                    fault_pages=fp,
                    regexes=tuple(data.get("regexes") or ()),
                    examples=tuple(data.get("examples") or ()),
                    whitelist=tuple(data.get("whitelist") or ()),
                    rows=rows,
                    source=data.get("source", "cache"),
                )
            except (json.JSONDecodeError, KeyError, TypeError) as exc:
                logger.warning("cache read failed for %s: %s — re-detecting", manual_id, exc)

    doc = fitz.open(str(pdf_path))
    try:
        candidates = _locate_fault_pages_via_toc(doc)
        fault_pages = _select_fault_range(candidates, doc.page_count)
        if not fault_pages:
            logger.info("no TOC fault-list entry for %s — skipping", manual_id)
            return None

        logger.info(
            "TOC located fault pages for %s: %s (from %d candidates)",
            manual_id, fault_pages, len(candidates),
        )

        # Step 1.5: try table extraction shortcut. If we recover ≥10 plausible
        # codes from table first columns, the LLM call is unnecessary — the
        # vendor laid the data out structurally and we trust it.
        table_codes, table_rows = _table_first_column_codes(doc, fault_pages)
        if len(table_codes) >= 10:
            logger.info(
                "PyMuPDF tables yielded %d codes (%d rows) for %s — skipping LLM",
                len(table_codes), len(table_rows), manual_id,
            )
            literal = r"\b(?:" + "|".join(re.escape(c) for c in table_codes) + r")\b"
            result = FaultPattern(
                manual_id=manual_id,
                vendor_hint=None,
                fault_pages=fault_pages,
                regexes=(literal,),
                examples=tuple(table_codes[:10]),
                whitelist=tuple(sorted(set(table_codes))),
                rows=tuple(table_rows),
                source="toc+tables",
            )
            if cache_dir is not None:
                cache_dir.mkdir(parents=True, exist_ok=True)
                (cache_dir / f"{manual_id}.fault_pattern.json").write_text(
                    json.dumps(result.as_dict(), ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            return result

        if table_codes:
            logger.info(
                "table extraction returned only %d codes — falling back to LLM",
                len(table_codes),
            )

        llm_obj = llm or _build_detector_llm()
        regexes, examples = _llm_infer_regexes(llm_obj, doc, fault_pages)
        if not regexes:
            result = FaultPattern(
                manual_id=manual_id,
                vendor_hint=None,
                fault_pages=fault_pages,
                source="toc-only",
            )
        else:
            whitelist, active_regexes = _build_whitelist(doc, fault_pages, regexes, examples)
            if not whitelist:
                result = FaultPattern(
                    manual_id=manual_id,
                    vendor_hint=None,
                    fault_pages=fault_pages,
                    regexes=tuple(regexes),
                    examples=tuple(examples),
                    source="toc-only",
                )
            else:
                result = FaultPattern(
                    manual_id=manual_id,
                    vendor_hint=None,
                    fault_pages=fault_pages,
                    regexes=tuple(active_regexes),
                    examples=tuple(examples),
                    whitelist=tuple(whitelist),
                    source="toc+llm",
                )
    finally:
        doc.close()

    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / f"{manual_id}.fault_pattern.json").write_text(
            json.dumps(result.as_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return result


def extract_codes_with_pattern(
    text: str, pattern: FaultPattern | None
) -> tuple[str, ...]:
    if pattern is None or not pattern.whitelist:
        return ()
    compiled = _compile_safe(pattern.regexes)
    if not compiled:
        return ()
    whitelist = set(pattern.whitelist)
    found: set[str] = set()
    for p in compiled:
        for m in p.finditer(text):
            tok = m.group(0).strip()
            if tok in whitelist:
                found.add(tok)
    return tuple(sorted(found))
