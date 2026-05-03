import audioop
import base64
import asyncio
import json
import websockets
from fastapi import WebSocket, WebSocketDisconnect
from app.services.elevenlabs import get_signed_url


async def run_bridge(twilio_ws: WebSocket):
    """WebSocket bridge: Twilio ↔ ElevenLabs Agent"""
    await twilio_ws.accept()
    print("🔌 Twilio WebSocket connected")

    stream_sid = None

    try:
        signed_url = await get_signed_url()
        print("🔑 Connecting to ElevenLabs...")

        async with websockets.connect(signed_url) as eleven_ws:
            print("🤖 ElevenLabs connected")

            # Send bare init — Dashboard handles language/voice/first_message
            await eleven_ws.send(json.dumps({
                "type": "conversation_initiation_client_data"
            }))
            print("📤 Sent init to ElevenLabs")

            async def twilio_to_eleven():
                """Twilio (mulaw 8000) → PCM 16000 → ElevenLabs"""
                nonlocal stream_sid
                async for message in twilio_ws.iter_text():
                    try:
                        data  = json.loads(message)
                        event = data.get("event")

                        if event == "connected":
                            print("📡 Twilio stream connected")

                        elif event == "start":
                            stream_sid = data["start"]["streamSid"]
                            print(f"🎙️ Stream started: {stream_sid}")

                        elif event == "media":
                            if eleven_ws.state.name == "OPEN":
                                # mulaw 8000 → PCM 16000
                                mulaw_data = base64.b64decode(data["media"]["payload"])
                                pcm_data   = audioop.ulaw2lin(mulaw_data, 2)
                                pcm_16k, _ = audioop.ratecv(pcm_data, 2, 1, 8000, 16000, None)
                                pcm_b64    = base64.b64encode(pcm_16k).decode("utf-8")
                                await eleven_ws.send(json.dumps({
                                    "user_audio_chunk": pcm_b64
                                }))

                        elif event == "stop":
                            print("🛑 Stream stopped")
                            break

                    except Exception as e:
                        print(f"❌ Twilio→ElevenLabs error: {e}")

            async def eleven_to_twilio():
                """ElevenLabs (PCM 16000) → mulaw 8000 → Twilio"""
                async for message in eleven_ws:
                    try:
                        data     = json.loads(message)
                        msg_type = data.get("type")

                        if msg_type == "conversation_initiation_metadata":
                            meta = data.get("conversation_initiation_metadata_event", {})
                            print(f"✅ ElevenLabs ready — input: {meta.get('user_input_audio_format')}, output: {meta.get('agent_output_audio_format')}")

                        elif msg_type == "audio":
                            audio_b64 = data.get("audio_event", {}).get("audio_base_64")
                            if audio_b64 and stream_sid:
                                # PCM 16000 → mulaw 8000
                                pcm_data   = base64.b64decode(audio_b64)
                                pcm_8k, _  = audioop.ratecv(pcm_data, 2, 1, 16000, 8000, None)
                                mulaw_data = audioop.lin2ulaw(pcm_8k, 2)
                                mulaw_b64  = base64.b64encode(mulaw_data).decode("utf-8")
                                await twilio_ws.send_text(json.dumps({
                                    "event":     "media",
                                    "streamSid": stream_sid,
                                    "media":     {"payload": mulaw_b64}
                                }))

                        elif msg_type == "user_transcript":
                            transcript = data.get("user_transcription_event", {}).get("user_transcript", "")
                            if transcript:
                                print(f"👤 User: {transcript}")

                        elif msg_type == "agent_response":
                            response = data.get("agent_response_event", {}).get("agent_response", "")
                            if response:
                                print(f"🤖 Auris: {response}")

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
                        print(f"❌ ElevenLabs→Twilio error: {e}")

            await asyncio.gather(
                twilio_to_eleven(),
                eleven_to_twilio()
            )

    except WebSocketDisconnect:
        print("📵 Twilio disconnected")
    except Exception as e:
        print(f"❌ Bridge error: {e}")
    finally:
        print("🔌 Bridge closed")