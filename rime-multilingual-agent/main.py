import logging
from typing import AsyncIterable
from dataclasses import dataclass
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    ModelSettings,
    RoomOutputOptions,
    WorkerOptions,
    cli,
    metrics,
    stt,
)
from livekit.plugins import silero, deepgram, rime
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit import rtc


logger = logging.getLogger("multilingual-agent")


load_dotenv()


@dataclass
class LanguageConfig:
    """Configuration for TTS settings per language"""

    speaker: str
    lang: str
    model: str = "arcana"
    

class MultilingualAgent(Agent):
    """A multilingual voice agent that detects user language and responds accordingly."""

    # Language mappings for cleaner configuration
    LANGUAGE_CONFIGS = {
        "en": LanguageConfig(speaker="celeste", lang="eng"),
        "es": LanguageConfig(speaker="astra", lang="spa"),
        "fr": LanguageConfig(speaker="livet_aurelie", lang="fra"),
        "de": LanguageConfig(speaker="lorelei", lang="ger"),
    }

    SUPPORTED_LANGUAGES = list(LANGUAGE_CONFIGS.keys())

    def __init__(self) -> None:
        super().__init__(instructions=self._get_instructions())
        self._current_language = "en"

    def _get_instructions(self) -> str:
        """Get agent instructions in a clean, maintainable format."""
        return (
            "You are a voice assistant powered by Rime's text-to-speech technology. "
            "You are here to showcase Rime's natural, expressive, and multilingual voice capabilities. "
            "You respond in the same language the user speaks in. "
            "You support English, Spanish, French, and German. "
            "If the user speaks in any other language, respond in English and politely let them know: "
            "'I only support English, Spanish, French, and German. Please speak in one of these languages.' "
            "Keep your responses concise and to the point since this is a voice conversation. "
            "Do not use emojis, asterisks, markdown, or other special characters in your responses. "
            "You are curious, friendly, and have a sense of humor."
        )

    async def stt_node(
        self, audio: AsyncIterable[rtc.AudioFrame], model_settings: ModelSettings
    ) -> AsyncIterable[stt.SpeechEvent]:
        """
        Override STT node to detect language and update TTS configuration dynamically.

        This method intercepts speech events to detect language changes and updates
        the TTS settings to match the detected language for natural voice output.
        """
        default_stt = super().stt_node(audio, model_settings)

        async for event in default_stt:
            # Process transcript events to detect language
            if self._is_transcript_event(event):
                await self._handle_language_detection(event)

            yield event

    def _is_transcript_event(self, event: stt.SpeechEvent) -> bool:
        """Check if event is a transcript event with language information."""
        return (
            event.type
            in [
                stt.SpeechEventType.INTERIM_TRANSCRIPT,
                stt.SpeechEventType.FINAL_TRANSCRIPT,
            ]
            and event.alternatives
        )

    async def _handle_language_detection(self, event: stt.SpeechEvent) -> None:
        """Handle language detection and TTS configuration updates."""
        detected_language = event.alternatives[0].language

        if detected_language and detected_language != self._current_language:
            logger.info(
                f"Language changed from {self._current_language} to {detected_language}"
            )
            self._current_language = detected_language
            self._update_tts_for_language(detected_language)

    def _update_tts_for_language(self, language: str) -> None:
        """Update TTS configuration based on detected language."""
        config = self.LANGUAGE_CONFIGS.get(language, self.LANGUAGE_CONFIGS["en"])

        self.session.tts.update_options(
            model=config.model,
            speaker=config.speaker,
            lang=config.lang,
        )

    async def on_enter(self) -> None:
        """Called when the agent session starts. Generate initial greeting."""
        self.session.generate_reply(instructions="Greet the user and introduce yourself as a voice assistant powered by Rime's text-to-speech technology. Ask how you can help them.")


def prewarm(proc: JobProcess) -> None:
    """Preload VAD model for faster startup."""
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext) -> None:
    """Main entry point for the multilingual agent worker."""
    ctx.log_context_fields = {"room": ctx.room.name}

    # Configure session with multilingual support
    session = AgentSession(
        stt=deepgram.STT(model="nova-3-general", language="multi"),
        llm="openai/gpt-4o",
        tts=rime.TTS(model="arcana", speaker="celeste"),
        turn_detection=MultilingualModel(),
    )

    # Set up metrics collection
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent) -> None:
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage() -> None:
        """Log usage summary on shutdown."""
        summary = usage_collector.get_summary()
        logger.info(f"Usage summary: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Start the agent session
    agent = MultilingualAgent()
    await session.start(
        agent=agent,
        room=ctx.room,
        room_output_options=RoomOutputOptions(transcription_enabled=True),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
