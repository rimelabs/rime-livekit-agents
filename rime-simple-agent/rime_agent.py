import logging
import random
from typing import AsyncIterable

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentSession,
    AutoSubscribe,
    JobContext,
    JobProcess,
    ModelSettings,
    tts,
    metrics,
    RoomInputOptions,
    WorkerOptions,
    cli,
)
from livekit.agents.voice import MetricsCollectedEvent
from livekit.plugins import (
    openai,
    noise_cancellation,
    rime,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from livekit.agents.tokenize import tokenizer
from agent_configs import VOICE_CONFIGS
from custom_pronunciations import (
    CustomPronunciationMap,
    DictCustomPronunciationsSource,
    load_custom_pronunciations,
    rewrite_tts_stream,
)


load_dotenv()
logger = logging.getLogger("voice-agent")

VOICE_NAMES = ["hank", "celeste"]
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_TRANSCRIPT_MODEL = "gpt-4o-transcribe"
VOICE = random.choice(VOICE_NAMES)

# Prototype mock map. Swap for APICustomPronunciationsSource() once the
# SpeechQA 2.0 backend is live; until then a literal dict is the fastest
# way to iterate on which pronunciations matter. Keys are input_text
# (lowercase; matching is case-insensitive at runtime).
MOCK_CUSTOM_PRONUNCIATIONS: dict[str, str] = {
    "lisinopril": "l0Is1Inxpr0Il",
    "pfizer": "f0Iz1@r",
    "whopper": "w1Ap@r",
}


def prewarm(proc: JobProcess):
    """Initialize VAD model for voice activity detection."""
    proc.userdata["vad"] = silero.VAD.load()


class RimeAssistant(Agent):
    """Voice assistant agent for Rime platform."""

    def __init__(self, custom_pronunciations: CustomPronunciationMap) -> None:
        super().__init__(instructions=VOICE_CONFIGS[VOICE]["llm_prompt"])
        self._custom_pronunciations = custom_pronunciations

    async def tts_node(
        self, text: AsyncIterable[str], model_settings: ModelSettings
    ) -> AsyncIterable[rtc.AudioFrame]:
        # Pre-TTS rewrite: every text chunk the LLM produces passes
        # through here before reaching the TTS engine. rewrite_tts_stream
        # buffers into sentences so tokens split across chunks don't
        # silently miss matches.
        rewritten = rewrite_tts_stream(text, self._custom_pronunciations)
        async for frame in Agent.default.tts_node(self, rewritten, model_settings):
            yield frame


async def entrypoint(ctx: JobContext):
    """Set up and start the voice assistant session."""
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    await ctx.wait_for_participant()

    prons = await load_custom_pronunciations(
        DictCustomPronunciationsSource(MOCK_CUSTOM_PRONUNCIATIONS)
    )

    rime_tts = rime.TTS(**VOICE_CONFIGS[VOICE]["tts_options"])
    session = AgentSession(
        stt=openai.STT(
            model=OPENAI_TRANSCRIPT_MODEL,
        ),
        llm=openai.LLM(model=OPENAI_MODEL),
        tts=rime_tts,
        vad=ctx.proc.userdata["vad"],
        turn_detection=MultilingualModel(),
    )
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info("Usage: %s", summary)

    ctx.add_shutdown_callback(log_usage)

    await session.start(
        room=ctx.room,
        agent=RimeAssistant(custom_pronunciations=prons),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    # No pre-rewrite here — RimeAssistant.tts_node applies
    # custom pronunciations to every outbound sentence, including this one.
    await session.say(VOICE_CONFIGS[VOICE]["intro_phrase"])


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
