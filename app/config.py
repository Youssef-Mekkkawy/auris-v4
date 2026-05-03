import os
from dotenv import load_dotenv

load_dotenv()

# Twilio
ACCOUNT_SID    = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN     = os.getenv("TWILIO_AUTH_TOKEN")
PHONE_NUMBER   = os.getenv("TWILIO_PHONE_NUMBER", "+19342212531")
API_KEY        = os.getenv("TWILIO_API_KEY")
API_SECRET     = os.getenv("TWILIO_API_SECRET")

# ElevenLabs
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID       = os.getenv("ELEVEN_VOICE_ID", "EGYKu1CV0vikeTYK5zoc")
AGENT_ID       = os.getenv("ELEVENLABS_AGENT_ID")

# Cloudflare
CLOUDFLARE_URL = os.getenv("CLOUDFLARE_URL", "")