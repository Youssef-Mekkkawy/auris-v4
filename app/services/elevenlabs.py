import httpx
from app.config import AGENT_ID, ELEVEN_API_KEY


async def get_signed_url() -> str:
    """Get signed WebSocket URL from ElevenLabs"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.elevenlabs.io/v1/convai/conversation/token?agent_id={AGENT_ID}",
            headers={"xi-api-key": ELEVEN_API_KEY}
        )
        data = resp.json()
        token = data.get("token")
        print(f"🔑 Got token: {token[:30]}...")
        return f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={AGENT_ID}&token={token}"