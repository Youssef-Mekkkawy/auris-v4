import subprocess
import threading
import time
import re
import sys
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

ENV_FILE = ".env"

# ── Config ──
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+19342212531")

cloudflare_url = None
twilio_client = Client(ACCOUNT_SID, AUTH_TOKEN)


def extract_url(line: str) -> str:
    match = re.search(r'https://[a-z0-9\-]+\.trycloudflare\.com', line)
    return match.group(0) if match else None


def update_env(key: str, value: str):
    """Update or add key in .env file"""
    lines = []
    found = False

    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            found = True
            break

    if not found:
        lines.append(f"{key}={value}\n")

    with open(ENV_FILE, "w") as f:
        f.writelines(lines)
    # ← ده السطر المهم — بيحدث os.environ مباشرة
    os.environ[key] = value

    print(f"✅ .env updated: {key}={value}")


# def update_twilio_webhook(url: str):
#     """Update Twilio phone number voice webhook using Twilio library"""
#     print(f"📞 Updating Twilio webhook...")

#     webhook_url = f"{url}/call"

#     try:
#         # Get all phone numbers
#         incoming_numbers = twilio_client.incoming_phone_numbers.list()

#         # Find our number
#         phone_sid = None
#         for number in incoming_numbers:
#             if number.phone_number == PHONE_NUMBER:
#                 phone_sid = number.sid
#                 print(f"✅ Found phone SID: {phone_sid}")
#                 break

#         if not phone_sid:
#             print(f"❌ Phone number {PHONE_NUMBER} not found in Twilio account")
#             return

#         # Update webhook
#         twilio_client.incoming_phone_numbers(phone_sid).update(
#             voice_url=webhook_url,
#             voice_method="POST"
#         )

#         print(f"✅ Twilio webhook updated: {webhook_url}")

#     except Exception as e:
#         print(f"❌ Failed to update Twilio webhook: {e}")
def update_twilio_webhook(url: str):
    """Update Twilio phone number voice webhook using Twilio library"""
    print(f"📞 Updating Twilio webhook...")

    webhook_url = f"{url}/call"
    fallback_url = f"{url}/call"

    try:
        # Get all phone numbers
        incoming_numbers = twilio_client.incoming_phone_numbers.list()

        # Find our number
        phone_sid = None
        for number in incoming_numbers:
            if number.phone_number == PHONE_NUMBER:
                phone_sid = number.sid
                print(f"✅ Found phone SID: {phone_sid}")
                break

        if not phone_sid:
            print(f"❌ Phone number {PHONE_NUMBER} not found")
            return

        # Update voice webhook + fallback
        twilio_client.incoming_phone_numbers(phone_sid).update(
            voice_url=webhook_url,
            voice_method="POST",
            voice_fallback_url=fallback_url,
            voice_fallback_method="POST"
        )

        print(f"✅ Voice webhook updated:  {webhook_url}")
        print(f"✅ Fallback webhook updated: {fallback_url}")

    except Exception as e:
        print(f"❌ Failed to update Twilio webhook: {e}")


def run_tunnel():
    """Start Cloudflare tunnel and capture URL"""
    global cloudflare_url
    print("🌐 Starting Cloudflare tunnel...")

    proc = subprocess.Popen(
        "cloudflared tunnel --url http://localhost:8000",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    for line in proc.stdout:
        line = line.strip()
        url = extract_url(line)
        if url and cloudflare_url is None:
            cloudflare_url = url
            update_env("CLOUDFLARE_URL", url)
            print(f"\n🎉 Tunnel URL: {url}")
            update_twilio_webhook(url)


def run_fastapi():
    """Start FastAPI server"""
    print("⚡ Starting FastAPI...")
    subprocess.run(
        f"{sys.executable} -m uvicorn main:app --reload --port 8000",
        shell=True
    )


def main():
    print("\n" + "="*50)
    print("   🤖 Auris — Starting Services")
    print("="*50 + "\n")

    # Step 1: Start tunnel in background
    t_tunnel = threading.Thread(target=run_tunnel, daemon=True)
    t_tunnel.start()

    # Step 2: Wait for tunnel URL
    print("⏳ Waiting for Cloudflare tunnel URL...")
    timeout = 30
    start = time.time()
    while time.time() - start < timeout:
        if cloudflare_url:
            break
        time.sleep(1)

    if not cloudflare_url:
        print("❌ Tunnel failed. Check cloudflared installation.")
        sys.exit(1)

    print(f"\n✅ All ready!")
    print(f"   URL    : {cloudflare_url}")
    print(f"   Browser: {cloudflare_url}/")
    print(f"   Webhook: {cloudflare_url}/call\n")

    # Step 3: Start FastAPI (blocking)
    run_fastapi()


if __name__ == "__main__":
    main()
