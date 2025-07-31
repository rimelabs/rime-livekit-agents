from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
)
from livekit.plugins import deepgram, openai, rime


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    agent = Agent(
        instructions="You are a friendly voice assistant built by LiveKit.",
    )

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=rime.TTS(model="mist", speaker="default"),
    )

    await session.start(agent=agent, room=ctx.room)
    await session.generate_reply(instructions="greet the user and ask about their day")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
