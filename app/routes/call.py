from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from app.services.bridge import run_bridge
import os
import json

router = APIRouter()

# ── Transcript WebSocket connections ──
transcript_clients: list[WebSocket] = []


async def broadcast_transcript(msg_type: str, text: str):
    """Send transcript message to all connected browser clients"""
    if not transcript_clients:
        return
    payload = json.dumps({"type": msg_type, "text": text})
    dead = []
    for ws in transcript_clients:
        try:
            await ws.send_text(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        transcript_clients.remove(ws)


@router.post("/call", response_class=HTMLResponse)
async def handle_call(request: Request):
    """Twilio webhook — returns TwiML with WebSocket stream"""
    form      = await request.form()
    call_sid  = form.get("CallSid", "unknown")
    print(f"\n{'='*40}")
    print(f"📞 Incoming call! SID: {call_sid}")

    cloudflare_url = os.getenv("CLOUDFLARE_URL", "")
    if not cloudflare_url:
        print("❌ CLOUDFLARE_URL is empty!")
        return HTMLResponse(
            content="""<?xml version="1.0" encoding="UTF-8"?>
            <Response><Say>Server configuration error.</Say></Response>""",
            media_type="application/xml"
        )

    ws_url     = cloudflare_url.replace("https://", "wss://")
    stream_url = f"{ws_url}/media-stream"
    print(f"🔗 Stream URL: {stream_url}")

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Connect>
            <Stream url="{stream_url}"/>
        </Connect>
    </Response>"""

    return HTMLResponse(content=twiml, media_type="application/xml")


@router.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    """WebSocket bridge: Twilio ↔ ElevenLabs"""
    await run_bridge(websocket, broadcast_transcript)


@router.websocket("/ws/transcript")
async def transcript_ws(websocket: WebSocket):
    """Browser client connects here to receive live transcript"""
    await websocket.accept()
    transcript_clients.append(websocket)
    print(f"🖥️ Browser connected to transcript WS ({len(transcript_clients)} clients)")
    try:
        while True:
            # keep connection alive — browser just listens
            await websocket.receive_text()
    except WebSocketDisconnect:
        transcript_clients.remove(websocket)
        print(f"🖥️ Browser disconnected ({len(transcript_clients)} clients left)")