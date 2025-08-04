import logging
import random

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    AutoSubscribe,
    JobContext,
    JobProcess,
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
    deepgram,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from sentence_tokenizer import ArcanaSentenceTokenizer
from livekit.agents.tokenize import tokenizer
from agent_configs import VOICE_CONFIGS


load_dotenv()
logger = logging.getLogger("voice-agent")

VOICE_NAMES = ["hank", "celeste"]
# randomly select a voice from the list
VOICE = random.choice(VOICE_NAMES)


def prewarm(proc: JobProcess):
    """Initialize VAD model for voice activity detection."""
    proc.userdata["vad"] = silero.VAD.load()


class RimeAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=VOICE_CONFIGS[VOICE]["llm_prompt"])


async def entrypoint(ctx: JobContext):
    """Set up and start the voice assistant session."""
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    await ctx.wait_for_participant()

    rime_tts = rime.TTS(**VOICE_CONFIGS[VOICE]["tts_options"])
    rime_tts = tts.StreamAdapter(
        tts=rime_tts, sentence_tokenizer=ArcanaSentenceTokenizer(min_sentence_len=1000)
    )
    if VOICE_CONFIGS[VOICE].get("sentence_tokenizer"):
        sentence_tokenizer = VOICE_CONFIGS[VOICE].get("sentence_tokenizer")
        if not isinstance(sentence_tokenizer, tokenizer.SentenceTokenizer):
            raise TypeError(
                f"Expected sentence_tokenizer to be an instance of tokenizer.SentenceTokenizer, got {type(sentence_tokenizer)}"
            )
        rime_tts = tts.StreamAdapter(
            tts=rime_tts, sentence_tokenizer=sentence_tokenizer
        )

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=openai.LLM(model="gpt-4o-mini"),
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
        agent=RimeAssistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )
    await session.say(VOICE_CONFIGS[VOICE]["intro_phrase"])


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
