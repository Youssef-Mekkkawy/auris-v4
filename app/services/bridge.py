import audioop
import base64
import asyncio
import json
import os
import httpx
import websockets
from fastapi import WebSocket, WebSocketDisconnect


async def get_signed_url() -> str:
    agent_id       = os.getenv("ELEVENLABS_AGENT_ID")
    eleven_api_key = os.getenv("ELEVEN_API_KEY")

    print(f"🔍 ELEVENLABS_AGENT_ID = '{agent_id}'")
    print(f"🔍 ELEVEN_API_KEY = '{eleven_api_key[:10]}...' " if eleven_api_key else "❌ ELEVEN_API_KEY is empty!")

    if not agent_id or not eleven_api_key:
        raise ValueError("❌ Missing ELEVENLABS_AGENT_ID or ELEVEN_API_KEY in .env")

    async with httpx.AsyncClient() as client:
        print(f"📡 Fetching signed URL from ElevenLabs...")
        resp = await client.get(
            f"https://api.elevenlabs.io/v1/convai/conversation/token?agent_id={agent_id}",
            headers={"xi-api-key": eleven_api_key}
        )
        print(f"📡 ElevenLabs response status: {resp.status_code}")

        if resp.status_code != 200:
            print(f"❌ ElevenLabs error: {resp.text}")
            raise ValueError(f"ElevenLabs API error: {resp.status_code} — {resp.text}")

        data  = resp.json()
        token = data.get("token")

        if not token:
            print(f"❌ No token in response: {data}")
            raise ValueError("No token received from ElevenLabs")

        print(f"✅ Got token: {token[:30]}...")
        url = f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={agent_id}&token={token}"
        print(f"✅ Signed URL built successfully")
        return url


async def run_bridge(twilio_ws: WebSocket):
    await twilio_ws.accept()
    print("✅ Twilio WebSocket accepted")

    stream_sid = None

    try:
        print("🔄 Getting signed URL...")
        signed_url = await get_signed_url()

        print(f"🔄 Connecting to ElevenLabs WebSocket...")
        async with websockets.connect(signed_url) as eleven_ws:
            print("✅ ElevenLabs WebSocket connected!")

            await eleven_ws.send(json.dumps({
                "type": "conversation_initiation_client_data"
            }))
            print("📤 Sent init message to ElevenLabs")

            async def twilio_to_eleven():
                nonlocal stream_sid
                print("🔄 twilio_to_eleven: starting loop...")
                async for message in twilio_ws.iter_text():
                    try:
                        data  = json.loads(message)
                        event = data.get("event")

                        if event == "connected":
                            print("✅ Twilio stream connected")

                        elif event == "start":
                            stream_sid = data["start"]["streamSid"]
                            print(f"✅ Stream started: {stream_sid}")

                        elif event == "media":
                            if eleven_ws.state.name == "OPEN":
                                mulaw_data = base64.b64decode(data["media"]["payload"])
                                pcm_data   = audioop.ulaw2lin(mulaw_data, 2)
                                pcm_16k, _ = audioop.ratecv(pcm_data, 2, 1, 8000, 16000, None)
                                pcm_b64    = base64.b64encode(pcm_16k).decode("utf-8")
                                await eleven_ws.send(json.dumps({
                                    "user_audio_chunk": pcm_b64
                                }))
                            else:
                                print(f"⚠️ ElevenLabs WS state: {eleven_ws.state.name} — skipping audio")

                        elif event == "stop":
                            print("🛑 Stream stopped by Twilio")
                            break

                        else:
                            print(f"⚠️ Unknown Twilio event: {event}")

                    except Exception as e:
                        print(f"❌ twilio_to_eleven error: {e}")

            async def eleven_to_twilio():
                print("🔄 eleven_to_twilio: starting loop...")
                async for message in eleven_ws:
                    try:
                        data     = json.loads(message)
                        msg_type = data.get("type")

                        if msg_type == "conversation_initiation_metadata":
                            meta = data.get("conversation_initiation_metadata_event", {})
                            print(f"✅ ElevenLabs ready!")
                            print(f"   input format : {meta.get('user_input_audio_format')}")
                            print(f"   output format: {meta.get('agent_output_audio_format')}")

                        elif msg_type == "audio":
                            audio_b64 = data.get("audio_event", {}).get("audio_base_64")
                            if audio_b64 and stream_sid:
                                pcm_data   = base64.b64decode(audio_b64)
                                pcm_8k, _  = audioop.ratecv(pcm_data, 2, 1, 16000, 8000, None)
                                mulaw_data = audioop.lin2ulaw(pcm_8k, 2)
                                mulaw_b64  = base64.b64encode(mulaw_data).decode("utf-8")
                                await twilio_ws.send_text(json.dumps({
                                    "event":     "media",
                                    "streamSid": stream_sid,
                                    "media":     {"payload": mulaw_b64}
                                }))
                            elif not stream_sid:
                                print("⚠️ Audio received but stream_sid not set yet!")

                        elif msg_type == "user_transcript":
                            transcript = data.get("user_transcription_event", {}).get("user_transcript", "")
                            if transcript:
                                print(f"👤 User said: {transcript}")

                        elif msg_type == "agent_response":
                            response = data.get("agent_response_event", {}).get("agent_response", "")
                            if response:
                                print(f"🤖 Auris: {response}")

                        elif msg_type == "interruption":
                            print("⚡ Interruption detected — clearing Twilio buffer")
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

                        else:
                            print(f"⚠️ Unknown ElevenLabs message type: {msg_type}")

                    except Exception as e:
                        print(f"❌ eleven_to_twilio error: {e}")

            print("🔄 Starting asyncio.gather...")
            await asyncio.gather(
                twilio_to_eleven(),
                eleven_to_twilio()
            )

    except WebSocketDisconnect:
        print("📵 Twilio WebSocket disconnected")
    except ValueError as e:
        print(f"❌ Config error: {e}")
    except Exception as e:
        print(f"❌ Bridge error: {type(e).__name__}: {e}")
    finally:
        print("🔌 Bridge closed\n")