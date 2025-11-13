import logging
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    RoomOutputOptions,
    RunContext,
    UserInputTranscribedEvent,
    WorkerOptions,
    cli,
    metrics,
)
from livekit.agents.llm import function_tool
from livekit.plugins import silero, deepgram, rime
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.plugins import noise_cancellation

logger = logging.getLogger("basic-agent")
load_dotenv()


class MyAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="Your name is Kelly. You would interact with users via voice. "
            "with that in mind keep your responses concise and to the point. "
            "do not use emojis, asterisks, markdown, or other special characters in your responses. "
            "You are curious and friendly, and have a sense of humor.",
        )
        self.current_language = "en"

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
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm="openai/gpt-4o-mini",
        tts=rime.TTS(model="arcana", speaker="astra"),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
    )

    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    @session.on("user_input_transcribed")
    def on_transcript(ev: UserInputTranscribedEvent):
        logger.info(f"Transcript: {ev}")
        if ev.is_final and ev.language:
            detected_lang = ev.language
            if detected_lang == "es":
                session.tts.update_options(
                    model="arcana",
                    speaker="eris",
                    lang="spa",
                )
            elif detected_lang == "fr":
                session.tts.update_options(
                    model="arcana",
                    speaker="destin",
                    lang="fra",
                )
            elif detected_lang == "de":
                session.tts.update_options(
                    model="arcana",
                    speaker="runa",
                    lang="ger",
                )
            else:
                session.tts.update_options(
                    model="arcana",
                    speaker="andromeda",
                    lang="eng",
                )
            logger.info(f"Detected language: {detected_lang}")

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    agent_instance = MyAgent()
    await session.start(
        agent=agent_instance,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
        room_output_options=RoomOutputOptions(transcription_enabled=True),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
