
# Rime Python Voice Agent

<p>
  •
  <a href="https://docs.livekit.io/agents/overview/">LiveKit Agents Docs</a>
  •
  <a href="https://livekit.io/cloud">LiveKit Cloud</a>
</p>

A set of Livekit agents using hyper realistic `mistv2` and `arcana` [Rime.ai](https://www.rime.ai/) tts models.

**⚠️Note** This uses a modified version of the Livekit Rime client to properly send over `arcana` specific paramters.
Do not use `arcana` in a production Livekit agent until these changes are merged upstream.

## Local Setup

Clone the repository, install dependencies to a virtual environment, and download relevant model files (turn detection)

```console
# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python rime_agent.py download-files
```

Set up the environment by copying `.env.example` to `.env` and filling in the required values:

- `OPENAI_API_KEY`
- `RIME_API_KEY`

Run the agent in console mode. This will NOT interact with livekit servers or a UI, it is just for debugging
 agent code, llm prompts, and testing voices.

```bash
python rime_agent.py console
```

## Livekit Server Setup
To connect to your livekit server, add in the following env vars:
- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`

## Prompt engineering

Create a new voice, configs, and prompt in `voice_configs.py` then set the value of `VOICE` in the agent file.

## Optional next steps

If you want to deploy your agent to a production environment (see for example the [Rime homepage demo](https://rime.ai/)), you'll want to do the following:

1. Add a frontend and connect it to LiveKit ([documentation](https://docs.livekit.io/agents/start/voice-ai/#connect-to-playground))
2. Deploy your agent with Render or another orchestration service ([documentation](https://docs.livekit.io/agents/ops/deployment/))
