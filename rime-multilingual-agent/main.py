import logging
from typing import AsyncIterable
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    ModelSettings,
    RoomOutputOptions,
    RunContext,
    WorkerOptions,
    cli,
    metrics,
    stt,
)
from livekit.agents.llm import function_tool
from livekit.plugins import silero, deepgram, rime
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.plugins import noise_cancellation
from livekit import rtc


logger = logging.getLogger("basic-agent")
load_dotenv()


class MultilingualAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="Your name is Kelly. You would interact with users via voice. "
            "with that in mind keep your responses concise and to the point. "
            "do not use emojis, asterisks, markdown, or other special characters in your responses. "
            "You are curious and friendly, and have a sense of humor."
            "always give output in english",
        )
        self._current_language = "en"

    async def stt_node(
        self, audio: AsyncIterable[rtc.AudioFrame], model_settings: ModelSettings
    ) -> AsyncIterable[stt.SpeechEvent]:
        """
        Override STT node to detect and log language from speech events.
        """
        # Get the default STT node implementation
        default_stt = super().stt_node(audio, model_settings)

        # Process each speech event and extract language info
        async for event in default_stt:
            if (
                event.type
                in [
                    stt.SpeechEventType.INTERIM_TRANSCRIPT,
                    stt.SpeechEventType.FINAL_TRANSCRIPT,
                ]
                and event.alternatives
            ):
                logger.info(f"Speech event: {event}")
                detected_language = event.alternatives[0].language
                if detected_language and detected_language != self._current_language:
                    logger.info(f"Detected language: {detected_language}")
                    self._current_language = detected_language
                    # self.session.tts.update_options(language=detected_language)

            yield event

    async def on_enter(self):
        self.session.generate_reply()

    @function_tool
    async def lookup_weather(
        self, context: RunContext, location: str, latitude: str, longitude: str
    ):
        """Called when the user asks for weather related information."""
        logger.info(f"Looking up weather for {location}")
        return "sunny with a temperature of 70 degrees."


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}
    session = AgentSession(
        stt=deepgram.STT(model="nova-3-general", language="multi"),
        llm="openai/gpt-4o-mini",
        tts=rime.TTS(model="arcana", speaker="marlu"),
        turn_detection=MultilingualModel(),
    )

    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    agent_instance = MultilingualAgent()
    await session.start(
        agent=agent_instance,
        room=ctx.room,
        room_output_options=RoomOutputOptions(transcription_enabled=True),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
