from fastapi import APIRouter
from fastapi.responses import JSONResponse
from twilio.rest import Client
from app.config import ACCOUNT_SID, AUTH_TOKEN, PHONE_NUMBER, CLOUDFLARE_URL

router   = APIRouter()
_client  = Client(ACCOUNT_SID, AUTH_TOKEN)


@router.get("/make-call")
async def make_call():
    """Trigger outbound call to Twilio Browser Client"""
    call = _client.calls.create(
        to="client:youssef",
        from_=PHONE_NUMBER,
        url=f"{CLOUDFLARE_URL}/call"
    )
    print(f"📞 Calling browser... SID: {call.sid}")
    return JSONResponse({"call_sid": call.sid, "status": call.status})