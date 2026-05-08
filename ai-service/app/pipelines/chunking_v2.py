"""Structure-aware chunking (Phase 6 rework — skeleton only).

Replaces the fixed-size chunker (`chunking.py`) with a layout-aware
pipeline so that procedures stay together, warnings are tagged, and
parent-child relationships let the retriever return precise children
while the LLM gets the full procedure as context.

Status: **interface + dataclass scaffolding only**. The detection
heuristics (`detect_sections`) are stubbed and will be filled in once
real PDFs arrive. Until then `chunk_pdf_structured` falls back to
single-page sections so the rest of the pipeline (DB schema, retrieval,
RAG v2) can be wired and tested against the synthetic generator output.

Cross-validation strategy (per user 2026-05-04):
- Run this on `scripts/generate_manuals.py` PDFs first.
- When the 5 real manuals arrive, swap `manuals/` and re-run the same
  ingest → KPI eval. Layout heuristics must generalize across all 5
  without per-manual hard-coding.
"""

from __future__ import annotations

import logging
import re
import statistics
import uuid
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

SectionType = Literal["procedure", "warning", "spec", "narrative", "table"]


# Error code patterns covering all five real manuals' formats:
#   - `E-NNN`, `EQ-001`, `ALM-12`  (prefix-NN — synthetic + Mitsubishi/Siemens style)
#   - `40747, Access Error`         (NNNNN, Title — ABB event log style)
# Both produce the canonical code string (no comma, no trailing title).
_ERROR_CODE_RE = re.compile(r"\b[A-Z]{1,4}-\d{2,4}\b")
_ABB_EVENT_RE = re.compile(r"\b(\d{4,6})(?=,\s+[A-Z])")
# More permissive ABB-style match for *queries* — users type "error 40747" with
# no trailing comma+title. Used only by extract_error_codes_from_query so the
# strict manual-text version stays free of false positives like chapter numbers.
_ABB_EVENT_RE_QUERY = re.compile(r"\b(\d{4,6})\b")
# Vendor-mnemonic candidate pattern for queries (Yaskawa "FAn", "oFA10",
# Schneider "OCF", "SrI2", Mitsubishi "AL.30", Rockwell "F040", etc.).
# This regex is intentionally permissive — the caller MUST intersect with a
# DB-derived known-codes set to avoid prose word leakage.
_MNEMONIC_RE_QUERY = re.compile(r"\b[A-Za-z][A-Za-z0-9.\-_]{1,18}\b")


def _extract_error_codes(text: str) -> tuple[str, ...]:
    """Union of prefix-style and ABB event-log codes, deduped, sorted.

    Strict — for ingest-time extraction from manual body text. Requires the
    ABB ', Title' suffix so chapter numbers like 'Section 1500' don't end up
    in the code list.
    """
    codes: set[str] = set(_ERROR_CODE_RE.findall(text))
    codes.update(_ABB_EVENT_RE.findall(text))
    return tuple(sorted(codes))


def extract_error_codes_from_query(text: str) -> tuple[str, ...]:
    """Permissive variant for runtime queries.

    Returns a SUPERSET of plausible code tokens — strict prefix-style codes,
    bare 4-6 digit numbers, AND any short alphanumeric mnemonic. The caller
    (PreFilter) MUST intersect this against the known-codes table to drop
    English words / model numbers that look like fault codes. Without that
    filter prose tokens like "the" would leak through.
    """
    codes: set[str] = set(_ERROR_CODE_RE.findall(text))
    codes.update(_ABB_EVENT_RE_QUERY.findall(text))
    codes.update(_MNEMONIC_RE_QUERY.findall(text))
    return tuple(sorted(codes))


@dataclass(frozen=True)
class Section:
    """One logical region of a manual after layout analysis.

    A section may span multiple pages. `page_start`/`page_end` are
    inclusive 1-indexed page numbers. `heading_path` records the
    hierarchical heading chain (e.g. ["3", "3.2", "3.2.1 Calibration"])
    so retrieval can surface meaningful breadcrumbs.
    """

    section_id: str
    manual_id: str
    equipment_id: str
    section_type: SectionType
    heading_path: tuple[str, ...]
    page_start: int
    page_end: int
    text: str
    error_codes: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        d = asdict(self)
        d["heading_path"] = list(self.heading_path)
        d["error_codes"] = list(self.error_codes)
        return d


@dataclass(frozen=True)
class Chunk:
    """Child chunk used at retrieval time.

    `parent_section_id` lets the RAG layer fetch the full parent
    section as LLM context after retrieving the precise child.
    """

    chunk_id: str
    parent_section_id: str
    manual_id: str
    equipment_id: str
    section_type: SectionType
    heading_path: tuple[str, ...]
    page: int
    chunk_index: int
    chunk_text: str
    error_codes: tuple[str, ...] = ()
    source_file: str = ""

    def as_dict(self) -> dict:
        d = asdict(self)
        d["heading_path"] = list(self.heading_path)
        d["error_codes"] = list(self.error_codes)
        return d


@dataclass
class ChunkingResult:
    sections: list[Section] = field(default_factory=list)
    chunks: list[Chunk] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Detection — heuristics generalize across the 5 real manuals
# (ABB / FANUC / Mitsubishi / LS / Siemens). Per-manual hard-coding is
# avoided; everything keys off relative font statistics computed per doc.
# Falls back to one-section-per-page when heading detection produces nothing.
# ---------------------------------------------------------------------------


_HEADING_SIZE_RATIO = 1.15  # span > body * 1.15 → strong heading
_INLINE_BOLD_MIN_RATIO = 1.0  # bold span >= body size → inline sub-heading candidate
_INLINE_HEADING_MAX_LEN = 80  # bold lines longer than this are body, not headings
_INLINE_HEADING_MIN_LEN = 3  # one/two-char "headings" are noise
_TOC_LEADER_RATIO = 0.30  # page text with >=30% '.' chars is a TOC page
_CHROME_REPEAT_RATIO = 0.7  # text repeated on >=70% of pages is header/footer
_CHROME_MIN_LEN = 10  # short repeating words ("Detail", "(2)") are NOT chrome
_WARNING_PREFIXES = ("WARNING", "CAUTION", "DANGER", "NOTE", "NOTICE")
_NUMBERED_STEP_RE = re.compile(r"^\s*\d+[\.\)]\s+\S")


def _detect_body_size(size_chars: Counter[float]) -> float:
    """Pick the body font size from a {size: char_count} histogram.

    Plain mode is unstable when the top two sizes are within 30% of each
    other (LS Electric: 11pt 40% vs 10.5pt 37%). In that case use a
    char-weighted mean of the top two so we land between them and the
    HEADING_SIZE_RATIO threshold still excludes both.
    """
    if not size_chars:
        return 10.0
    top = sorted(size_chars.items(), key=lambda kv: -kv[1])[:2]
    if len(top) == 2 and top[1][1] / top[0][1] >= 0.7:
        s0, n0 = top[0]
        s1, n1 = top[1]
        return (s0 * n0 + s1 * n1) / (n0 + n1)
    return top[0][0]


def _detect_repeating_chrome(page_lines: list[list[str]]) -> set[str]:
    """Identify header/footer lines that repeat across most pages.

    Filters:
      - Lines must be 10–120 chars (short repeating words like "Detail",
        "(2)", "Consequences" are real body content, not chrome).
      - Must repeat on ≥70% of pages (was 50% — caught ABB sub-headings).
    Catches things like ABB's "3HAC020738-001 Revision: K" on every page.
    """
    if not page_lines:
        return set()
    counter: Counter[str] = Counter()
    for lines in page_lines:
        seen_on_page: set[str] = set()
        for line in lines:
            stripped = line.strip()
            if _CHROME_MIN_LEN <= len(stripped) <= 120:
                seen_on_page.add(stripped)
        for text in seen_on_page:
            counter[text] += 1
    threshold = max(2, int(len(page_lines) * _CHROME_REPEAT_RATIO))
    return {text for text, n in counter.items() if n >= threshold}


def _is_toc_page(text: str) -> bool:
    """TOC pages are dominated by leader dots ('. . . . . . 69')."""
    if not text:
        return False
    dot_chars = text.count(".")
    return dot_chars / max(len(text), 1) >= _TOC_LEADER_RATIO


def _is_bold(font_name: str) -> bool:
    """Match both PostScript ('Arial-BoldMT') and CSV ('Arial,Bold') styles."""
    fl = font_name.lower()
    return "bold" in fl or "black" in fl or "heavy" in fl


@dataclass
class _Line:
    """Layout-flattened line — one PDF text line with aggregate font signals."""

    text: str
    page: int
    max_size: float
    is_bold: bool


def _flatten_lines(doc: fitz.Document) -> tuple[list[_Line], Counter[float]]:
    """Walk the document once; emit one _Line per PDF text line."""
    lines: list[_Line] = []
    size_chars: Counter[float] = Counter()
    for page_num in range(doc.page_count):
        page = doc[page_num]
        for blk in page.get_text("dict").get("blocks", []):
            if blk.get("type") != 0:
                continue
            for line in blk.get("lines", []):
                spans = line.get("spans") or []
                if not spans:
                    continue
                line_text = "".join(s.get("text", "") for s in spans).strip()
                if not line_text:
                    continue
                max_sz = 0.0
                bold = False
                for s in spans:
                    sz = round(s.get("size", 0.0), 1)
                    nch = len(s.get("text", ""))
                    if nch:
                        size_chars[sz] += nch
                    if sz > max_sz:
                        max_sz = sz
                    if _is_bold(s.get("font", "")):
                        bold = True
                lines.append(
                    _Line(text=line_text, page=page_num + 1, max_size=max_sz, is_bold=bold)
                )
    return lines, size_chars


def _classify_line(line: _Line, body_size: float) -> str:
    """Return one of: 'heading_strong', 'heading_inline', 'body', 'caption'.

    Inline (bold-only) headings get extra constraints — without them,
    every bolded inline phrase becomes a section anchor and we end up
    with hundreds of 1-character "sections".
    """
    text = line.text.strip()
    if line.max_size > body_size * _HEADING_SIZE_RATIO:
        return "heading_strong"
    if (
        line.is_bold
        and line.max_size >= body_size * _INLINE_BOLD_MIN_RATIO
        and _INLINE_HEADING_MIN_LEN <= len(text) <= _INLINE_HEADING_MAX_LEN
        and not text.endswith((".", "?", "!", ":"))  # complete sentences are body, not headings
    ):
        return "heading_inline"
    if line.max_size < body_size * 0.85:
        return "caption"
    return "body"


def _classify_section_type(heading_text: str, body_text: str) -> SectionType:
    """Decide section_type from heading + first lines of body.

    Order matters — warning/error checks come first because their
    keywords often co-occur with procedure markers.
    """
    head_upper = heading_text.upper().strip()
    if any(head_upper.startswith(p) for p in _WARNING_PREFIXES):
        return "warning"
    sample = (body_text[:400] or "").splitlines()
    for prefix in _WARNING_PREFIXES:
        if any(line.strip().upper().startswith(prefix) for line in sample[:3]):
            return "warning"
    # ABB event log: heading is "40747, Access Error"
    if _ABB_EVENT_RE.search(heading_text) or _ERROR_CODE_RE.search(heading_text):
        return "procedure"  # event-log entries are recovery procedures
    # Numbered step run in the first few body lines
    numbered = sum(1 for line in sample[:6] if _NUMBERED_STEP_RE.match(line))
    if numbered >= 2:
        return "procedure"
    return "narrative"


def detect_sections(
    doc: fitz.Document,
    *,
    manual_id: str,
    equipment_id: str,
) -> list[Section]:
    """Layout-aware section detection across the 5 real-manual formats.

    Pipeline:
      1. Flatten PDF to one _Line per text line; collect font size histogram.
      2. Compute body font size (mode, with LS-style two-mode fallback).
      3. Identify repeating header/footer lines and skip them.
      4. Identify TOC pages (leader-dot dominated) and skip them.
      5. Walk lines; treat heading_strong/heading_inline as section starts.
      6. For each section, classify type (warning/procedure/narrative) and
         extract error codes.

    Falls back to one-narrative-per-page when no headings are detected
    (preserves behavior on synthetic manuals that lack font signals).
    """
    lines, size_chars = _flatten_lines(doc)
    if not lines:
        return []

    body_size = _detect_body_size(size_chars)

    # Build per-page line lists for chrome detection (small-line dedupe).
    per_page: dict[int, list[str]] = {}
    for line in lines:
        per_page.setdefault(line.page, []).append(line.text)
    chrome = _detect_repeating_chrome(list(per_page.values()))
    toc_pages = {pg for pg, ls in per_page.items() if _is_toc_page("\n".join(ls))}

    # Pass 1: collect heading anchors in document order.
    anchors: list[tuple[int, _Line, str]] = []  # (line_idx, line, kind)
    for idx, line in enumerate(lines):
        if line.page in toc_pages or line.text in chrome:
            continue
        kind = _classify_line(line, body_size)
        if kind in ("heading_strong", "heading_inline"):
            anchors.append((idx, line, kind))

    if not anchors:
        return _fallback_page_sections(doc, manual_id=manual_id, equipment_id=equipment_id)

    # Pass 2: walk anchors → sections. Each anchor heads a section that
    # spans up to (but not including) the next anchor. heading_path is
    # built from the most recent strong heading + this heading.
    sections: list[Section] = []
    last_strong: str | None = None
    for a_pos, (line_idx, anchor, kind) in enumerate(anchors):
        next_idx = anchors[a_pos + 1][0] if a_pos + 1 < len(anchors) else len(lines)
        body_lines = [
            li.text
            for li in lines[line_idx + 1 : next_idx]
            if li.page not in toc_pages and li.text not in chrome
        ]
        body_text = "\n".join(body_lines).strip()
        if kind == "heading_strong":
            last_strong = anchor.text
        heading_path = tuple(h for h in (last_strong, anchor.text) if h)
        # Deduplicate when inline heading == strong (first anchor case).
        heading_path = tuple(dict.fromkeys(heading_path))
        section_type = _classify_section_type(anchor.text, body_text)
        full_text = f"{anchor.text}\n{body_text}".strip()
        if not full_text:
            continue
        page_end = lines[next_idx - 1].page if next_idx > line_idx else anchor.page
        sections.append(
            Section(
                section_id=str(uuid.uuid4()),
                manual_id=manual_id,
                equipment_id=equipment_id,
                section_type=section_type,
                heading_path=heading_path,
                page_start=anchor.page,
                page_end=page_end,
                text=full_text,
                error_codes=_extract_error_codes(full_text),
            )
        )

    if not sections:
        return _fallback_page_sections(doc, manual_id=manual_id, equipment_id=equipment_id)
    return sections


def _fallback_page_sections(
    doc: fitz.Document,
    *,
    manual_id: str,
    equipment_id: str,
) -> list[Section]:
    """One narrative section per page. Used when font-based detection fails
    (e.g. synthetic PDFs without varied fonts)."""
    sections: list[Section] = []
    for page_num in range(doc.page_count):
        page = doc[page_num]
        text = page.get_text().strip()
        if not text:
            continue
        sections.append(
            Section(
                section_id=str(uuid.uuid4()),
                manual_id=manual_id,
                equipment_id=equipment_id,
                section_type="narrative",
                heading_path=(f"page-{page_num + 1}",),
                page_start=page_num + 1,
                page_end=page_num + 1,
                text=text,
                error_codes=_extract_error_codes(text),
            )
        )
    return sections


# ---------------------------------------------------------------------------
# Child chunking inside a parent section
# ---------------------------------------------------------------------------


def _split_text(text: str, size: int, overlap: int) -> list[str]:
    if not text:
        return []
    if size <= 0:
        raise ValueError("chunk size must be positive")
    if overlap < 0 or overlap >= size:
        raise ValueError("overlap must be in [0, size)")
    step = size - overlap
    pieces: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        pieces.append(text[i : i + size])
        i += step
    return pieces


def chunk_section(
    section: Section,
    *,
    child_size: int,
    child_overlap: int,
    source_file: str,
) -> list[Chunk]:
    """Split a parent section into retrieval-time child chunks.

    Procedure/warning/spec sections are kept whole when short enough so
    the LLM sees the full step list rather than a fragment. Narrative
    sections always get fixed-size split.
    """
    keep_whole = (
        section.section_type in ("procedure", "warning", "spec")
        and len(section.text) <= child_size * 2
    )
    pieces = [section.text] if keep_whole else _split_text(section.text, child_size, child_overlap)

    chunks: list[Chunk] = []
    for idx, piece in enumerate(pieces):
        chunks.append(
            Chunk(
                chunk_id=str(uuid.uuid4()),
                parent_section_id=section.section_id,
                manual_id=section.manual_id,
                equipment_id=section.equipment_id,
                section_type=section.section_type,
                heading_path=section.heading_path,
                page=section.page_start,  # children inherit start page; refine when we span pages
                chunk_index=idx,
                chunk_text=piece,
                error_codes=section.error_codes,
                source_file=source_file,
            )
        )
    return chunks


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def chunk_pdf_structured(
    pdf_path: str | Path,
    *,
    manual_id: str,
    equipment_id: str,
    child_size: int = 600,
    child_overlap: int = 80,
) -> ChunkingResult:
    """Run structure-aware chunking against a single PDF.

    Returns both parent sections and child chunks. Callers persist
    sections (for parent-fetch at LLM time) and embed only the children.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(path)

    doc = fitz.open(str(path))
    try:
        sections = detect_sections(doc, manual_id=manual_id, equipment_id=equipment_id)
    finally:
        doc.close()

    chunks: list[Chunk] = []
    for sec in sections:
        chunks.extend(
            chunk_section(
                sec,
                child_size=child_size,
                child_overlap=child_overlap,
                source_file=path.name,
            )
        )

    logger.info(
        "structured chunking complete",
        extra={
            "file": path.name,
            "sections": len(sections),
            "chunks": len(chunks),
            "manual_id": manual_id,
        },
    )
    return ChunkingResult(sections=sections, chunks=chunks)
