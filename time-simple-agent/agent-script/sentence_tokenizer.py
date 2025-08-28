import re
import functools
from dataclasses import dataclass
from typing import List, Tuple

from livekit.agents.tokenize import token_stream, tokenizer

_sentence_pattern = re.compile(r".+?[,，.。!！?？:：]", re.DOTALL)


@dataclass
class _TokenizerOptions:
    language: str
    min_sentence_len: int
    stream_context_len: int


class ArcanaSentenceTokenizer(tokenizer.SentenceTokenizer):
    """Tokenizer that segments text into sentences with configurable length and context."""

    def __init__(
        self,
        *,
        language: str = "english",
        min_sentence_len: int = 10,
        stream_context_len: int = 10,
    ) -> None:
        self._config = _TokenizerOptions(
            language=language,
            min_sentence_len=min_sentence_len,
            stream_context_len=stream_context_len,
        )

    def tokenize(self, text: str, *, language: str | None = None) -> List[str]:
        """Split text into sentences, returning only the sentence strings."""
        sentences = self.sentence_segmentation(text)
        return [sentence[0] for sentence in sentences]

    def stream(self, *, language: str | None = None) -> tokenizer.SentenceStream:
        """Create a buffered stream for processing sentences with context."""
        return token_stream.BufferedSentenceStream(
            tokenizer=functools.partial(self.sentence_segmentation),
            min_token_len=self._config.min_sentence_len,
            min_ctx_len=self._config.stream_context_len,
        )

    def sentence_segmentation(self, text: str) -> List[Tuple[str, int, int]]:
        """Split text into sentences with their start and end positions."""
        # arcana doesn't like unicode quotes
        text = text.replace("\u2018", "'").replace("\u2019", "'")
        result = []
        start_pos = 0

        for match in _sentence_pattern.finditer(text):
            sentence = match.group(0)
            end_pos = match.end()
            sentence = sentence.strip()
            if sentence:
                result.append((sentence, start_pos, end_pos))
            start_pos = end_pos

        if start_pos < len(text):
            sentence = text[start_pos:].strip()
            if sentence:
                result.append((sentence, start_pos, len(text)))

        return result
