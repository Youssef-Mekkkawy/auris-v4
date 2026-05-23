
""" Enable overrides  """
from elevenlabs import ElevenLabs
import os
from dotenv import load_dotenv

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVEN_API_KEY"))

client.conversational_ai.agents.update(
    agent_id=os.getenv("ELEVENLABS_AGENT_ID"),
    platform_settings={
        "overrides": {
            "conversation_config_override": {
                "agent": {
                    "first_message": True,
                    "language": True,
                    "prompt": {"prompt": True},
                },
                "tts": {"voice_id": True},
            },
        },
    },
)

print("✅ Overrides enabled!")