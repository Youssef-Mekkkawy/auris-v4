from fastapi import APIRouter
from fastapi.responses import JSONResponse
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from app.config import ACCOUNT_SID, API_KEY, API_SECRET

router = APIRouter()


@router.get("/token")
async def get_token():
    """Generate Twilio Browser Client JWT token"""
    token = AccessToken(ACCOUNT_SID, API_KEY, API_SECRET, identity="youssef")
    grant = VoiceGrant(outgoing_application_sid=None, incoming_allow=True)
    token.add_grant(grant)
    return JSONResponse({"token": token.to_jwt()})