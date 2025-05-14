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
    cli
)
from livekit.agents.voice import MetricsCollectedEvent
from livekit.plugins import (
    cartesia,
    openai,
    noise_cancellation,
    rime,
    silero,
)
from livekit.agents.tokenize import tokenizer

from livekit.plugins.turn_detector.multilingual import MultilingualModel

from agent_configs import VOICE_CONFIGS

load_dotenv()
logger = logging.getLogger("voice-agent")

VOICE_NAMES = ["hank", "celeste"]
# randomly select a voice from the list
VOICE = "celeste"

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

class RimeAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=VOICE_CONFIGS[VOICE]["llm_prompt"])


async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for the first participant to connect
    participant = await ctx.wait_for_participant()

    logger.info(f"Running Rime voice agent for voice config {VOICE} and participant {participant.identity}")

    # rime_tts = rime.TTS(
    #     **VOICE_CONFIGS[VOICE]["tts_options"]
    # )
    
    cartesia_tts = cartesia.TTS(model="sonic-2", voice="bf0a246a-8642-498a-9950-80c35e9276b5")

    if VOICE_CONFIGS[VOICE].get("sentence_tokenizer"):
        sentence_tokenizer = VOICE_CONFIGS[VOICE].get("sentence_tokenizer")
        if not isinstance(sentence_tokenizer, tokenizer.SentenceTokenizer):
            raise TypeError(
                f"Expected sentence_tokenizer to be an instance of tokenizer.SentenceTokenizer, got {type(sentence_tokenizer)}"
            )
        cartesia_tts = tts.StreamAdapter(tts=cartesia_tts, sentence_tokenizer=sentence_tokenizer)

    session = AgentSession(
        stt=openai.STT(),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia_tts,
        vad=ctx.proc.userdata["vad"],
        turn_detection=MultilingualModel()
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

    await session.start(
        room=ctx.room,
        agent=RimeAssistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        )
    )

    await session.say(VOICE_CONFIGS[VOICE]["intro_phrase"])

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
