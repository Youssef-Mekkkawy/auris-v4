from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi import WebSocket
from app.config import CLOUDFLARE_URL
from app.services.bridge import run_bridge

router = APIRouter()


@router.post("/call", response_class=HTMLResponse)
async def handle_call(request: Request):
    """Twilio webhook — returns TwiML with WebSocket stream"""
    form    = await request.form()
    call_sid = form.get("CallSid", "unknown")
    print(f"📞 Call connected! SID: {call_sid}")

    ws_url = CLOUDFLARE_URL.replace("https://", "wss://")

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Connect>
            <Stream url="{ws_url}/media-stream"/>
        </Connect>
    </Response>"""

    return HTMLResponse(content=twiml, media_type="application/xml")


@router.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    """WebSocket bridge: Twilio ↔ ElevenLabs"""
    await run_bridge(websocket)