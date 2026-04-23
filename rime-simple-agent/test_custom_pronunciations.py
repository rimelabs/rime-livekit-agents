"""
Tests for the custom_pronunciations plugin.

Runs under pytest. Exercises the dict source, the apply rewrite, and the
API source with a stubbed aiohttp response so no network is touched.
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from custom_pronunciations import (
    APICustomPronunciationsSource,
    DictCustomPronunciationsSource,
    apply_custom_pronunciations,
    load_custom_pronunciations,
    rewrite_tts_stream,
)


# ---------------------------------------------------------------------------
# apply_custom_pronunciations — rewrite behavior
# ---------------------------------------------------------------------------


SAMPLE_PRONS = {
    # Canonical single-token word (would also have oov_word_id server-side).
    "lisinopril": "l0Is1Inxpr0Il",
    # Literal with trailing punctuation — oov_word_id NULL server-side.
    "dr.": "d1aktx0r",
    # Literal phrase with a space + digits — oov_word_id NULL server-side.
    "lisinopril 10mg": "l0Is1Inxpr0Il t1En m0Il0Igr@m",
}


def test_rewrite_picks_up_canonical_word():
    out = apply_custom_pronunciations(
        "Take your lisinopril at night.", SAMPLE_PRONS
    )
    assert out == "Take your {l0Is1Inxpr0Il} at night."


def test_rewrite_picks_up_literal_with_trailing_punctuation():
    # "Dr." — the original \b-based regex would fail here because the
    # position after the '.' is not a word boundary. Lookaround on \w
    # handles it.
    out = apply_custom_pronunciations("Dr. Smith will see you now.", SAMPLE_PRONS)
    assert out == "{d1aktx0r} Smith will see you now."


def test_rewrite_picks_up_literal_phrase():
    out = apply_custom_pronunciations(
        "Prescribe Lisinopril 10mg daily.", SAMPLE_PRONS
    )
    assert out == "Prescribe {l0Is1Inxpr0Il t1En m0Il0Igr@m} daily."


def test_longer_literal_wins_over_shorter_substring():
    # "Lisinopril 10mg" is a prefix-sharing superstring of "lisinopril".
    # The longer one must match first.
    out = apply_custom_pronunciations("Lisinopril 10mg please.", SAMPLE_PRONS)
    assert out == "{l0Is1Inxpr0Il t1En m0Il0Igr@m} please."


def test_case_insensitive_match():
    cases = [
        "LISINOPRIL is strong.",
        "lisinopril is strong.",
        "Lisinopril is strong.",
        "LiSiNoPrIl is strong.",
    ]
    for text in cases:
        out = apply_custom_pronunciations(text, SAMPLE_PRONS)
        assert out == "{l0Is1Inxpr0Il} is strong.", text


def test_no_match_passthrough():
    out = apply_custom_pronunciations(
        "Nothing in this sentence matches.", SAMPLE_PRONS
    )
    assert out == "Nothing in this sentence matches."


def test_empty_map_passthrough():
    out = apply_custom_pronunciations("Lisinopril.", {})
    assert out == "Lisinopril."


def test_does_not_match_inside_word():
    # "lisinoprilly" should NOT match "lisinopril" — the trailing `(?!\w)`
    # prevents partial-word hits.
    out = apply_custom_pronunciations("The word lisinoprilly is fake.", SAMPLE_PRONS)
    assert out == "The word lisinoprilly is fake."


# ---------------------------------------------------------------------------
# DictCustomPronunciationsSource
# ---------------------------------------------------------------------------


def test_dict_source_normalizes_keys_to_lowercase():
    source = DictCustomPronunciationsSource({"Lisinopril": "l0Is1Inxpr0Il"})
    prons = asyncio.run(source.load())
    assert prons == {"lisinopril": "l0Is1Inxpr0Il"}


def test_dict_source_accepts_pairs():
    source = DictCustomPronunciationsSource([("Dr.", "d1aktx0r")])
    prons = asyncio.run(source.load())
    assert prons == {"dr.": "d1aktx0r"}


# ---------------------------------------------------------------------------
# APICustomPronunciationsSource — stubbed aiohttp response
# ---------------------------------------------------------------------------


class _StubResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_a):
        return False

    def raise_for_status(self):
        return None

    async def json(self):
        return self._payload


class _StubSession:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload
        self.last_url: str | None = None
        self.last_headers: dict[str, str] | None = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_a):
        return False

    def get(self, url: str, headers: dict[str, str]):
        self.last_url = url
        self.last_headers = headers
        return _StubResponse(self._payload)


def test_api_source_projects_three_row_response(monkeypatch):
    payload = {
        "customPronunciations": [
            {
                "id": "cp-1",
                "inputText": "Lisinopril",
                "pronunciation": "l0Is1Inxpr0Il",
                "oovWordId": "oov-1",
                "customerContext": None,
                "createdAt": "2026-04-17T00:00:00Z",
                "updatedAt": "2026-04-17T00:00:00Z",
            },
            {
                "id": "cp-2",
                "inputText": "Dr.",
                "pronunciation": "d1aktx0r",
                "oovWordId": None,
                "customerContext": "title prefix",
                "createdAt": "2026-04-17T00:00:00Z",
                "updatedAt": "2026-04-17T00:00:00Z",
            },
            {
                "id": "cp-3",
                "inputText": "Lisinopril 10mg",
                "pronunciation": "l0Is1Inxpr0Il t1En m0Il0Igr@m",
                "oovWordId": None,
                "customerContext": None,
                "createdAt": "2026-04-17T00:00:00Z",
                "updatedAt": "2026-04-17T00:00:00Z",
            },
        ]
    }
    session = _StubSession(payload)

    import aiohttp

    monkeypatch.setattr(aiohttp, "ClientSession", lambda: session)

    source = APICustomPronunciationsSource(api_key="test-key")
    prons = asyncio.run(load_custom_pronunciations(source))

    assert prons == {
        "lisinopril": "l0Is1Inxpr0Il",
        "dr.": "d1aktx0r",
        "lisinopril 10mg": "l0Is1Inxpr0Il t1En m0Il0Igr@m",
    }
    assert session.last_url == "https://users.rime.ai/speech-qa/custom-pronunciations"
    assert session.last_headers["Authorization"] == "Bearer test-key"

    # Confirm the rewrite picks up all three after a real API-shaped load.
    rewritten = apply_custom_pronunciations(
        "Dr. Smith said Lisinopril 10mg not Lisinopril alone.", prons
    )
    assert rewritten == (
        "{d1aktx0r} Smith said {l0Is1Inxpr0Il t1En m0Il0Igr@m} "
        "not {l0Is1Inxpr0Il} alone."
    )


def test_api_source_rejects_missing_api_key(monkeypatch):
    monkeypatch.delenv("RIME_API_KEY", raising=False)
    with pytest.raises(ValueError):
        APICustomPronunciationsSource()


# ---------------------------------------------------------------------------
# rewrite_tts_stream — pre-TTS sentence-buffered rewrite
# ---------------------------------------------------------------------------


async def _async_iter(chunks):
    for c in chunks:
        yield c


async def _collect(agen):
    out = []
    async for item in agen:
        out.append(item)
    return out


def test_rewrite_tts_stream_across_chunked_tokens():
    # Simulate an LLM that emits a single input_text split across multiple
    # chunks. A naive per-chunk rewrite would miss this.
    chunks = [
        "Take your Lis",
        "inopril at night.",
        " Dr.",
        " Smith prescribed Lisinopril 10",
        "mg daily.",
    ]
    out = asyncio.run(
        _collect(rewrite_tts_stream(_async_iter(chunks), SAMPLE_PRONS))
    )
    # Sentences get joined into chunks of substantial length; every known
    # input_text is rewritten regardless of which chunk split it.
    joined = " ".join(out)
    assert "{l0Is1Inxpr0Il}" in joined, joined
    assert "{d1aktx0r}" in joined, joined
    assert "{l0Is1Inxpr0Il t1En m0Il0Igr@m}" in joined, joined
    # And the raw input_text strings are gone (case-insensitive check).
    assert "Lisinopril" not in joined
    assert "Dr." not in joined


def test_rewrite_tts_stream_empty_prons_passes_through():
    chunks = ["Hello there, how are you today?"]
    out = asyncio.run(_collect(rewrite_tts_stream(_async_iter(chunks), {})))
    assert " ".join(out).strip() == "Hello there, how are you today?"


def test_rewrite_tts_stream_empty_input():
    out = asyncio.run(_collect(rewrite_tts_stream(_async_iter([]), SAMPLE_PRONS)))
    assert out == []


def test_api_source_drops_rows_missing_required_fields(monkeypatch):
    payload = {
        "customPronunciations": [
            {"inputText": "Good", "pronunciation": "g1Ud"},
            {"inputText": "", "pronunciation": "b1@d"},  # missing inputText
            {"inputText": "NoPron", "pronunciation": None},  # missing pron
        ]
    }
    session = _StubSession(payload)

    import aiohttp

    monkeypatch.setattr(aiohttp, "ClientSession", lambda: session)

    source = APICustomPronunciationsSource(api_key="k")
    prons = asyncio.run(source.load())
    assert prons == {"good": "g1Ud"}
