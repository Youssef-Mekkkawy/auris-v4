import audioop
import base64
import asyncio
import json
import os
import httpx
import websockets
from fastapi import WebSocket, WebSocketDisconnect
from typing import Callable, Awaitable


async def get_signed_url() -> str:
    agent_id = os.getenv("ELEVENLABS_AGENT_ID")
    eleven_api_key = os.getenv("ELEVEN_API_KEY")

    print(f"🔍 ELEVENLABS_AGENT_ID = '{agent_id}'")

    if not agent_id or not eleven_api_key:
        raise ValueError("❌ Missing ELEVENLABS_AGENT_ID or ELEVEN_API_KEY")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://api.elevenlabs.io/v1/convai/conversation/token?agent_id={agent_id}",
            headers={"xi-api-key": eleven_api_key}
        )
        print(f"📡 ElevenLabs token status: {resp.status_code}")
        if resp.status_code != 200:
            raise ValueError(
                f"ElevenLabs API error: {resp.status_code} — {resp.text}")

        token = resp.json().get("token")
        if not token:
            raise ValueError("No token received from ElevenLabs")

        print(f"✅ Got token: {token[:30]}...")
        return f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={agent_id}&token={token}"


async def run_bridge(
    twilio_ws: WebSocket,
    broadcast: Callable[[str, str], Awaitable[None]] = None
):
    """WebSocket bridge: Twilio ↔ ElevenLabs Agent"""
    await twilio_ws.accept()
    print("✅ Twilio WebSocket accepted")

    stream_sid = None

    # helper — safe broadcast
    async def bcast(msg_type: str, text: str):
        if broadcast:
            try:
                await broadcast(msg_type, text)
            except Exception as e:
                print(f"⚠️ broadcast error: {e}")

    try:
        signed_url = await get_signed_url()
        print("🔄 Connecting to ElevenLabs WebSocket...")

        async with websockets.connect(signed_url) as eleven_ws:
            print("✅ ElevenLabs connected!")

            await eleven_ws.send(json.dumps({
                "type": "conversation_initiation_client_data"
            }))
            print("📤 Sent init to ElevenLabs")

            async def twilio_to_eleven():
                nonlocal stream_sid
                print("🔄 twilio_to_eleven: starting...")
                async for message in twilio_ws.iter_text():
                    try:
                        data = json.loads(message)
                        event = data.get("event")

                        if event == "connected":
                            print("✅ Twilio stream connected")

                        elif event == "start":
                            stream_sid = data["start"]["streamSid"]
                            print(f"✅ Stream started: {stream_sid}")

                        elif event == "media":
                            if eleven_ws.state.name == "OPEN":
                                mulaw_data = base64.b64decode(
                                    data["media"]["payload"])
                                pcm_data = audioop.ulaw2lin(mulaw_data, 2)
                                pcm_16k, _ = audioop.ratecv(
                                    pcm_data, 2, 1, 8000, 16000, None)
                                pcm_b64 = base64.b64encode(
                                    pcm_16k).decode("utf-8")
                                await eleven_ws.send(json.dumps({
                                    "user_audio_chunk": pcm_b64
                                }))

                        elif event == "stop":
                            print("🛑 Stream stopped")
                            break

                    except Exception as e:
                        print(f"❌ twilio_to_eleven error: {e}")

            async def eleven_to_twilio():
                print("🔄 eleven_to_twilio: starting...")
                async for message in eleven_ws:
                    try:
                        data = json.loads(message)
                        msg_type = data.get("type")

                        if msg_type == "conversation_initiation_metadata":
                            meta = data.get(
                                "conversation_initiation_metadata_event", {})
                            print(f"✅ ElevenLabs ready!")
                            print(
                                f"   input : {meta.get('user_input_audio_format')}")
                            print(
                                f"   output: {meta.get('agent_output_audio_format')}")

                        elif msg_type == "audio":
                            audio_b64 = data.get(
                                "audio_event", {}).get("audio_base_64")
                            if audio_b64 and stream_sid:
                                pcm_data = base64.b64decode(audio_b64)
                                pcm_8k, _ = audioop.ratecv(
                                    pcm_data, 2, 1, 16000, 8000, None)
                                mulaw_data = audioop.lin2ulaw(pcm_8k, 2)
                                mulaw_b64 = base64.b64encode(
                                    mulaw_data).decode("utf-8")
                                await twilio_ws.send_text(json.dumps({
                                    "event":     "media",
                                    "streamSid": stream_sid,
                                    "media":     {"payload": mulaw_b64}
                                }))

                        elif msg_type == "user_transcript":
                            transcript = data.get("user_transcription_event", {}).get(
                                "user_transcript", "")
                            if transcript:
                                print(f"👤 User: {transcript}")
                                # ← broadcast to browser
                                await bcast("user_transcript", transcript)

                        elif msg_type == "agent_response":
                            response = data.get("agent_response_event", {}).get(
                                "agent_response", "")
                            if response:
                                print(f"🤖 Auris: {response}")
                                # ← broadcast to browser
                                await bcast("agent_response", response)

                        elif msg_type == "interruption":
                            if stream_sid:
                                await twilio_ws.send_text(json.dumps({
                                    "event":     "clear",
                                    "streamSid": stream_sid
                                }))

                        elif msg_type == "ping":
                            await eleven_ws.send(json.dumps({
                                "type":     "pong",
                                "event_id": data.get("ping_event", {}).get("event_id")
                            }))

                    except Exception as e:
                        print(f"❌ eleven_to_twilio error: {e}")

            print("🔄 Starting asyncio.gather...")
            await asyncio.gather(
                twilio_to_eleven(),
                eleven_to_twilio()
            )

    except WebSocketDisconnect:
        print("📵 Twilio disconnected")
    except ValueError as e:
        print(f"❌ Config error: {e}")
    except Exception as e:
        print(f"❌ Bridge error: {type(e).__name__}: {e}")
    finally:
        print("🔌 Bridge closed\n")
