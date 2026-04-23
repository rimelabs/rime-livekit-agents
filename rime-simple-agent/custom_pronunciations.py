"""
Rime SpeechQA 2.0 custom pronunciations plugin for LiveKit agents.

Customers register (input_text, pronunciation) pairs in the billable-level
`custom_pronunciations` table. The agent rewrites outbound text so any
occurrence of `input_text` is wrapped in Rime's bracketed-phoneme escape
syntax ({l0Is1Inxpr0Il}), bypassing the engine's G2P lexicon lookup for
that span and guaranteeing the custom pronunciation.

Vocabs do nothing at request time in 2.0 — they're SpeechQA workflow,
share-link, and research artifacts only. The single runtime entry point
is `apply_custom_pronunciations(text, prons)`.

`input_text` is case-preserved server-side but matched case-insensitively
here (match_case is not in the v1 schema). Literals with punctuation or
spaces are supported: "Dr.", "AT&T", "Lisinopril 10mg".

Two sources:

- DictCustomPronunciationsSource — literal {input_text: phonemes} dict;
  no HTTP, no auth.
- APICustomPronunciationsSource — GET /speech-qa/custom-pronunciations against the
  Rime SpeechQA 2.0 customer API (billable-scoped via API key).

Typical use:

    from custom_pronunciations import (
        DictCustomPronunciationsSource,
        load_custom_pronunciations,
        apply_custom_pronunciations,
    )

    source = DictCustomPronunciationsSource({"Lisinopril": "l0Is1Inxpr0Il"})
    prons  = await load_custom_pronunciations(source)
    ready  = apply_custom_pronunciations("Take your lisinopril at night", prons)
    # -> "Take your {l0Is1Inxpr0Il} at night"
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
from abc import ABC, abstractmethod
from typing import AsyncGenerator, AsyncIterable, Dict, Iterable, Mapping, Tuple

logger = logging.getLogger("rime-custom-pronunciations")

# Resolved map keyed by lowercase input_text → Rime phoneme string.
CustomPronunciationMap = Dict[str, str]


class CustomPronunciationsSource(ABC):
    """Abstract source. Implementations return an {input_text: phonemes} dict."""

    @abstractmethod
    async def load(self) -> CustomPronunciationMap:
        ...


class DictCustomPronunciationsSource(CustomPronunciationsSource):
    """
    In-memory source. Pass a dict (or list of (input_text, phonemes) pairs).
    Keys are normalized to lowercase at load time; matching is case-insensitive.
    """

    def __init__(
        self, entries: Mapping[str, str] | Iterable[Tuple[str, str]]
    ) -> None:
        items = entries.items() if hasattr(entries, "items") else entries
        self._map: CustomPronunciationMap = {
            input_text.lower(): pron for input_text, pron in items
        }

    async def load(self) -> CustomPronunciationMap:
        return dict(self._map)


class APICustomPronunciationsSource(CustomPronunciationsSource):
    """
    Fetches the billable's custom pronunciations from the Rime SpeechQA 2.0
    customer API.

    Hits `GET {base_url}/speech-qa/custom-pronunciations` and projects the response to
    an {input_text_lower: phonemes} dict. The billable is determined from
    the API key; there is no vocab_id/vocab_key parameter — vocabs do
    nothing at runtime.
    """

    DEFAULT_BASE_URL = "https://users.rime.ai"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("RIME_API_KEY")
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        if not self.api_key:
            raise ValueError(
                "APICustomPronunciationsSource needs an api_key or RIME_API_KEY in the env"
            )

    async def load(self) -> CustomPronunciationMap:
        # Imported lazily so dict-only callers don't need aiohttp installed.
        # aiohttp is a transitive dep of livekit-agents, so it's present
        # when this path runs inside the agent.
        import aiohttp

        url = f"{self.base_url}/speech-qa/custom-pronunciations"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url, headers=headers) as resp:
                resp.raise_for_status()
                body = await resp.json()
        return _project_list_response(body)


def _project_list_response(body: dict) -> CustomPronunciationMap:
    """
    Project the `GET /speech-qa/custom-pronunciations` response into a lookup map.
    Shape per the SpeechQA 2.0 wire contract:

        {
          customPronunciations: [
            { id, inputText, pronunciation, oovWordId, customerContext,
              createdAt, updatedAt },
            ...
          ]
        }

    `oovWordId` is irrelevant at runtime — the plugin matches on
    `inputText` directly. Entries missing inputText or pronunciation are
    dropped silently.
    """
    out: CustomPronunciationMap = {}
    for row in body.get("customPronunciations") or []:
        input_text = (row.get("inputText") or "").strip()
        pron = row.get("pronunciation")
        if not input_text or not pron:
            continue
        out[input_text.lower()] = pron
    return out


def _compile_pattern(prons: CustomPronunciationMap) -> re.Pattern | None:
    """
    Build a case-insensitive alternation regex covering every input_text in
    the map. Keys are sorted descending by length so longer literals match
    before shorter ones that would otherwise shadow them ("Lisinopril 10mg"
    before "Lisinopril").

    Bounds use lookaround on word chars (`(?<!\\w)` / `(?!\\w)`) rather than
    `\\b`, so literals with trailing punctuation ("Dr.") and literals with
    spaces ("Lisinopril 10mg") match cleanly. `\\b` fails at the
    word/non-word boundary test when a literal ends in punctuation.
    """
    if not prons:
        return None
    keys = sorted(prons.keys(), key=len, reverse=True)
    escaped = [re.escape(k) for k in keys]
    return re.compile(
        r"(?<!\w)(" + "|".join(escaped) + r")(?!\w)", re.IGNORECASE
    )


def apply_custom_pronunciations(
    text: str, prons: CustomPronunciationMap
) -> str:
    """
    Rewrite `text` so every known input_text is replaced with Rime's
    bracketed phoneme escape syntax `{<phonemes>}`. Case-insensitive match
    and lookup. Returns the input unchanged if the map is empty.

    Spans inside existing `{...}` brackets are not re-rewritten — the
    alternation only fires on the literal characters of each input_text,
    and the lookarounds prevent partial-word hits.
    """
    pattern = _compile_pattern(prons)
    if pattern is None:
        return text

    def _replace(match: re.Match) -> str:
        key = match.group(0).lower()
        phonemes = prons.get(key)
        if phonemes is None:
            return match.group(0)
        return "{" + phonemes + "}"

    return pattern.sub(_replace, text)


async def load_custom_pronunciations(
    source: CustomPronunciationsSource,
) -> CustomPronunciationMap:
    """Thin convenience wrapper so call sites read cleanly."""
    prons = await source.load()
    logger.info("loaded %d custom pronunciations", len(prons))
    return prons


async def rewrite_tts_stream(
    text: AsyncIterable[str], prons: CustomPronunciationMap
) -> AsyncGenerator[str, None]:
    """
    Buffer an async text stream into sentences, rewrite each sentence via
    `apply_custom_pronunciations`, and yield rewritten sentences.

    Designed to slot into `Agent.tts_node`: the LLM emits tokens in small
    chunks ("Lis" + "inopril"), which would silently miss matches if
    rewritten chunk-by-chunk. Sentence-level buffering is the same unit
    the downstream TTS StreamAdapter uses, so there's no added latency
    beyond what the TTS pipeline already introduces for non-streaming
    engines.

    Usage:

        class MyAgent(Agent):
            def __init__(self, prons): ...
            async def tts_node(self, text, model_settings):
                rewritten = rewrite_tts_stream(text, self._prons)
                async for frame in Agent.default.tts_node(
                    self, rewritten, model_settings
                ):
                    yield frame
    """
    # Lazy import so tests that don't exercise this path don't need
    # livekit.agents in the import graph.
    from livekit.agents import tokenize

    sent_stream = tokenize.blingfire.SentenceTokenizer(
        retain_format=True
    ).stream()

    async def _pump() -> None:
        try:
            async for chunk in text:
                sent_stream.push_text(chunk)
        finally:
            sent_stream.end_input()

    pump_task = asyncio.create_task(_pump())
    try:
        async for sentence in sent_stream:
            yield apply_custom_pronunciations(sentence.token, prons)
    finally:
        await pump_task
