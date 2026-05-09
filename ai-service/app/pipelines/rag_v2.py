"""RAG v2 — Korean-output, parent-context, structured retrieval (skeleton).

Differs from `rag.py` (v1) in three ways:

1. **Retrieval**: delegates to `HybridRetriever` (pre-filter + BM25 + Vector
   + RRF + reranker) instead of vector-only similarity_search.
2. **Context window**: when an LLM call happens, the retriever returns
   precise child chunks but the prompt is built from each child's
   **parent section** so the model sees the full procedure.
3. **Korean enforcement**: response goes through a deterministic
   post-processing pass (`KoreanResponseRules`) so the structure is
   guaranteed regardless of LLM whim — fixed sections, numbered steps,
   manual citations.

Status: skeleton. `parent_loader` and the rule-based post-processor are
stubbed; LLM call mirrors v1's `/no_think` quirk for qwen3.5:9b. Wired
under a feature flag in the API layer (default off) until v2 retrieval
hits parity with v1 on the synthetic eval set.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from typing import Protocol

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import Settings, get_settings
from app.core.llm import get_llm
from app.core.vectorstore import VectorStore
from app.pipelines.chunking_v2 import Section
from app.pipelines.retrieval_v2 import (
    BM25Searcher,
    HybridRetriever,
    Hit,
    PreFilter,
    Reranker,
    VectorSearcher,
)
from app.schemas.search import GuideStep, RawChunk, SearchResponse, SourceRef

logger = logging.getLogger(__name__)

# Same Qwen3 quirk as v1 — `/no_think` in BOTH system and user content
# or the model returns empty for long prompts. See
# `project_qwen3_no_think.md` memory.
_NO_THINK = SystemMessage(content="/no_think")

# Mandatory Korean output skeleton enforced at both prompt time and
# parse time. Reviewer feedback: real industrial responses must be in
# Korean regardless of source manual language.
#
# Style decisions to keep qwen3.5:9b honest:
#   - No `<placeholder>` tokens in the skeleton — the model copies them
#     verbatim into output. Use plain instructions instead.
#   - Per-step source format is shown as a literal example so the model
#     produces real `(출처: <file>.pdf, p.<num>)` rather than the
#     placeholder `<매뉴얼>` it sees.
#   - "[관련 오류 코드]" is auto-filled by KoreanResponseRules from the
#     retrieved chunks' error_codes — model output for that section is
#     overwritten regardless of what it produced.
_KOREAN_SKELETON = """다음 매뉴얼 컨텍스트를 바탕으로 사용자의 질문에 한국어로 답하라.
출력은 반드시 아래 두 섹션을 포함해야 한다.

[원인]
한 문단으로 원인을 설명하라.

[조치 절차]
1. 첫 번째 조치 (출처: abb_irb_troubleshooting.pdf, p.234)
2. 두 번째 조치 (출처: abb_irb_troubleshooting.pdf, p.235)

규칙:
- 출처 표기는 위 예시와 동일하게 매 줄 끝에 `(출처: 파일명.pdf, p.페이지)` 형식으로 쓰라.
  파일명과 페이지는 컨텍스트 블록 머리의 `[매뉴얼: ..., 페이지: ...]`에서 그대로 가져와라.
- 모든 답변은 한국어로 작성하라 (영어 그대로 옮기지 말 것).
- 컨텍스트의 변수 자리표시자(`arg`, `<...>` 등)는 그대로 옮기지 말고 자연스럽게 풀어 쓰라.
- 컨텍스트에 없는 사실을 만들지 말라.
- "<...>", "..." 같은 자리표시자 문구를 출력에 포함하지 말라.
"""


class ParentLoader(Protocol):
    """Looks up the parent `Section` for a retrieval `Hit`."""

    def load(self, parent_section_id: str) -> Section | None: ...


@dataclass
class StoreParentLoader:
    """ParentLoader backed by `VectorStore.fetch_section`.

    Returns a `Section`-shaped object so the prompt builder gets the full
    parent text instead of just the retrieved child chunk. Uses a small
    LRU so the same section isn't re-fetched per query.
    """

    store: VectorStore

    def __post_init__(self) -> None:
        # tiny per-instance cache to avoid repeat fetches inside one query
        self._cache: dict[str, Section | None] = {}

    def load(self, parent_section_id: str) -> Section | None:
        if parent_section_id in self._cache:
            return self._cache[parent_section_id]
        row = self.store.fetch_section(parent_section_id)
        if not row:
            self._cache[parent_section_id] = None
            return None
        section = Section(
            section_id=row["section_id"],
            manual_id=row["manual_id"],
            equipment_id=row["equipment_id"],
            section_type=row["section_type"],
            heading_path=tuple(row["heading_path"] or ()),
            page_start=row["page_start"],
            page_end=row["page_end"],
            text=row["section_text"] or "",
            error_codes=tuple(row["error_codes"] or ()),
        )
        self._cache[parent_section_id] = section
        return section


# ---------------------------------------------------------------------------
# Korean response rules — deterministic, no extra LLM round-trip
# ---------------------------------------------------------------------------


@dataclass
class KoreanResponseRules:
    """Post-process the LLM raw output into a guaranteed structure.

    Runs purely on regex/string ops (no LLM calls) so it does not
    affect P95 latency. Cleans the typical qwen3.5:9b failure modes
    observed during AI-24:

    1. Placeholder leak — `<한 문단>`, `<조치>`, `<매뉴얼>`, `<페이지>`,
       trailing `...` from the prompt skeleton get copied verbatim.
    2. ABB `arg` placeholder — manual body uses literal `arg` for any
       variable, model sometimes emits sentences like "arg를 확인하라".
    3. Generic "매뉴얼" filename — model omits the real `<vendor>.pdf`
       even though context provides it.
    4. Prompt section leak — `## 컨텍스트`, `## 질문` headers occasionally
       show up at the tail.
    5. `[관련 오류 코드] 없음` even when retrieved chunks list real codes
       — fill this section deterministically from the hits.

    `normalize()` accepts an optional `code_hint` (codes harvested from
    retrieved chunks) so we can inject the correct list instead of
    trusting the model.
    """

    required_sections: tuple[str, ...] = ("[원인]", "[조치 절차]", "[관련 오류 코드]")

    # placeholder text fragments that should never appear in output
    _placeholder_re = re.compile(
        r"<[^>\n]{0,40}>"           # <한 문단>, <조치>, <매뉴얼>, <페이지>
        r"|^\s*\.\.\.\s*$"          # standalone "..." line
        r"|^\s*##\s*(?:컨텍스트|질문).*$"  # leaked prompt section header
        r"|^\s*비워\s*두?세요\.?\s*$" # leaked instruction "비워두세요"
        r"|^\s*이\s*섹션은\s*자동.*$" # leaked instruction line
        r"|\[관련 오류 코드\]\s*$",   # trailing empty header line
        re.MULTILINE,
    )

    # The model occasionally echoes the entire "규칙:" instruction block.
    # Strip from "규칙:" through the next blank line followed by "[" header
    # or end of text, whichever comes first.
    _rules_block_re = re.compile(
        r"^규칙\s*[::].*?(?=\n\s*\[|\Z)",
        re.DOTALL | re.MULTILINE,
    )

    # ABB-style variable placeholders that survive into LLM output
    _arg_re = re.compile(r"\barg\b", re.IGNORECASE)

    # `(출처: 매뉴얼, p.234)` — generic filename fallback that needs real name
    _generic_source_re = re.compile(
        r"(\(\s*출처\s*[::]\s*)매뉴얼(\s*,\s*p\.?\s*\d+\s*\))"
    )

    def normalize(
        self,
        raw: str,
        *,
        code_hint: list[str] | None = None,
        manual_filename_hint: str | None = None,
    ) -> str:
        text = raw.strip()

        # Step 0 — strip leaked "규칙:" instruction block before anything else
        text = self._rules_block_re.sub("", text)

        # Step 1 — drop placeholder fragments
        text = self._placeholder_re.sub("", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Step 2 — soften ABB `arg` placeholders to a generic Korean noun
        #          so the sentence still reads naturally
        text = self._arg_re.sub("해당 인자", text)

        # Step 3 — replace literal "매뉴얼" inside (출처: ...) with the
        #          most representative real filename (Top-1 hit)
        if manual_filename_hint:
            text = self._generic_source_re.sub(
                rf"\1{manual_filename_hint}\2", text,
            )

        # Step 4 — ensure every required header is present
        for header in self.required_sections:
            if header not in text:
                text += f"\n\n{header}\n"

        # Step 5 — overwrite the [관련 오류 코드] body with retrieved codes.
        #          Model output for this section is unreliable; we know the
        #          ground truth from the retriever.
        codes_str = ", ".join(dict.fromkeys(code_hint or [])) or "없음"
        text = self._replace_section_body(text, "[관련 오류 코드]", codes_str)

        return text.strip() + "\n"

    @staticmethod
    def _replace_section_body(text: str, header: str, body: str) -> str:
        """Replace whatever the model wrote between `header` and the next
        `[xxx]` header (or end of text) with `body`."""
        idx = text.find(header)
        if idx < 0:
            return text + f"\n\n{header}\n{body}\n"
        start = idx + len(header)
        # find next "[" that begins another section header
        rest = text[start:]
        nxt_match = re.search(r"\n\s*\[", rest)
        end = start + nxt_match.start() if nxt_match else len(text)
        return text[:start] + f"\n{body}\n" + text[end:]


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


@dataclass
class RagPipelineV2:
    settings: Settings
    llm: BaseChatModel
    retriever: HybridRetriever
    parent_loader: ParentLoader
    rules: KoreanResponseRules

    @classmethod
    def build(cls, settings: Settings | None = None) -> "RagPipelineV2":
        """Wire the full v2 pipeline.

        - `PreFilter.from_store()` loads the equipment-routing map and the
          known_codes whitelist from `manual_sections.error_codes`.
        - `BM25Searcher` receives that whitelist so the +10 identifier
          boost works for every vendor format (not just the legacy regex).
        - Reranker loads the bge-reranker-base weights lazily on first
          retrieve() call (~5s on 4060). HybridRetriever does not warmup
          here — caller can issue a "warmup" query if cold-start P95
          matters for the demo.
        """
        settings = settings or get_settings()
        store = VectorStore(settings)
        prefilter = PreFilter.from_store(store)
        retriever = HybridRetriever(
            pre_filter=prefilter,
            bm25=BM25Searcher(store=store, known_codes=prefilter.known_codes),
            vector=VectorSearcher(store=store),
            reranker=Reranker(),
            candidate_k=settings.v2_candidate_k,
            final_k=settings.v2_final_k,
        )
        return cls(
            settings=settings,
            llm=get_llm(settings),
            retriever=retriever,
            parent_loader=StoreParentLoader(store=store),
            rules=KoreanResponseRules(),
        )

    def search(
        self,
        query: str,
        *,
        equipment_id: str | None = None,
        top_k: int | None = None,
    ) -> SearchResponse:
        """Run hybrid retrieval + Korean LLM answer generation.

        `top_k` overrides `settings.v2_final_k` for this call only — the
        retriever's reranker still narrows from `candidate_k` candidates.
        """
        t0 = time.perf_counter()

        hits = self.retriever.retrieve(
            query,
            equipment_id=equipment_id,
            final_k=top_k,
        )
        if not hits:
            return SearchResponse(
                steps=[],
                raw_chunks=[],
                answer_text="관련 매뉴얼을 찾지 못했습니다",
                fallback=True,
                latency_ms=int((time.perf_counter() - t0) * 1000),
            )

        context = self._build_parent_context(hits)
        prompt = self._render_prompt(query, context)

        raw = self.llm.invoke(
            [_NO_THINK, HumanMessage(content=f"/no_think\n\n{prompt}")]
        ).content
        # Harvest deterministic hints from retrieval for post-processing —
        # don't trust the model for codes/filenames when we already know them.
        code_hint = self._collect_codes(hits)
        manual_filename_hint = f"{hits[0].manual_id}.pdf" if hits else None
        normalized = self.rules.normalize(
            raw,
            code_hint=code_hint,
            manual_filename_hint=manual_filename_hint,
        )
        steps = self._parse_steps(normalized)
        # Auto-attach a source to any step where the model omitted one.
        # Round-robin through retrieved hits so each step still cites a
        # real (manual, page) the user can verify.
        if hits:
            steps = self._attach_default_sources(steps, hits)

        return SearchResponse(
            steps=steps,
            raw_chunks=[self._hit_to_raw(h) for h in hits],
            answer_text=normalized,
            fallback=not steps,
            latency_ms=int((time.perf_counter() - t0) * 1000),
        )

    # ----- helpers -----

    def _attach_default_sources(
        self, steps: list[GuideStep], hits: list[Hit]
    ) -> list[GuideStep]:
        """For steps where the model omitted (출처: ...), assign one from
        the retrieved hits in rank order. Keeps every step verifiable."""
        out: list[GuideStep] = []
        for i, s in enumerate(steps):
            if s.source is not None:
                out.append(s)
                continue
            h = hits[min(i, len(hits) - 1)]
            out.append(
                GuideStep(
                    order=s.order,
                    action=s.action,
                    source=SourceRef(manual=f"{h.manual_id}.pdf", page=h.page),
                )
            )
        return out

    def _collect_codes(self, hits: list[Hit]) -> list[str]:
        """Pull error_codes from each hit's parent section.

        Order: by hit rank, deduped. The first hit usually contains the
        canonical row for the queried code; surrounding hits add adjacent
        codes from the same fault table.
        """
        codes: list[str] = []
        seen: set[str] = set()
        for h in hits:
            parent = self.parent_loader.load(h.parent_section_id)
            if parent is None:
                continue
            for c in parent.error_codes or ():
                if c in seen:
                    continue
                seen.add(c)
                codes.append(c)
        return codes

    def _build_parent_context(self, hits: list[Hit]) -> str:
        blocks: list[str] = []
        seen: set[str] = set()
        for h in hits:
            if h.parent_section_id in seen:
                continue
            seen.add(h.parent_section_id)
            parent = self.parent_loader.load(h.parent_section_id)
            text = parent.text if parent else h.chunk_text
            heading = " > ".join(parent.heading_path) if parent else " > ".join(h.heading_path)
            blocks.append(
                f"[매뉴얼: {h.manual_id}.pdf, 페이지: {h.page}, 섹션: {heading}]\n{text}"
            )
        return "\n\n---\n\n".join(blocks)

    def _render_prompt(self, query: str, context: str) -> str:
        return (
            f"{_KOREAN_SKELETON}\n\n"
            f"## 컨텍스트\n{context}\n\n"
            f"## 질문\n{query}\n"
        )

    def _parse_steps(self, text: str) -> list[GuideStep]:
        # Reuse v1's regex shape — the post-processed text follows the
        # same `N. action (출처: file.pdf, p.PAGE)` convention.
        from app.pipelines.rag import _STEP_RE  # local import to avoid cycle

        steps: list[GuideStep] = []
        for m in _STEP_RE.finditer(text):
            order = int(m.group(1))
            action = m.group(2).strip()
            file_, page = m.group("file"), m.group("page")
            source = (
                SourceRef(manual=file_.strip(), page=int(page)) if file_ and page else None
            )
            steps.append(GuideStep(order=order, action=action, source=source))
        return steps

    def _hit_to_raw(self, h: Hit) -> RawChunk:
        return RawChunk(
            chunk_id=h.chunk_id,
            manual_id=h.manual_id,
            equipment_id=h.equipment_id,
            page=h.page,
            chunk_text=h.chunk_text,
            similarity=round(h.score, 4),
        )


def _build_default_llm(settings: Settings | None = None) -> BaseChatModel:
    return get_llm(settings or get_settings())
