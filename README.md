<div align="center">

<br/>

```
 █████╗ ██╗   ██╗██████╗ ██╗███████╗
██╔══██╗██║   ██║██╔══██╗██║██╔════╝
███████║██║   ██║██████╔╝██║███████╗
██╔══██║██║   ██║██╔══██╗██║╚════██║
██║  ██║╚██████╔╝██║  ██║██║███████║
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝
```

### **Enterprise AI Voice Bot Platform**
*Built for Egypt & the MENA Region — Speaks the Dialect, Respects the Data*

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Laravel](https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white)](https://laravel.com)
[![Twilio](https://img.shields.io/badge/Twilio-F22F46?style=for-the-badge&logo=twilio&logoColor=white)](https://twilio.com)
[![Gemini](https://img.shields.io/badge/Gemini_Flash-8E75B2?style=for-the-badge&logo=googlebard&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)](https://ubuntu.com)

<br/>

[![License](https://img.shields.io/badge/License-Proprietary-red?style=flat-square)](./LICENSE)
[![Latency](https://img.shields.io/badge/Latency-%3C%203s-brightgreen?style=flat-square)]()
[![Dialect](https://img.shields.io/badge/Dialect-Egyptian%20Arabic-blue?style=flat-square)]()
[![Status](https://img.shields.io/badge/Status-MVP%20Active-success?style=flat-square)]()

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [The Problem It Solves](#-the-problem-it-solves)
- [Core Features](#-core-features)
- [System Architecture](#️-system-architecture--call-flow)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Environment Variables](#️-environment-variables)
- [Installation & Setup](#️-installation--setup)
- [KPIs & Success Metrics](#-kpis--success-metrics)
- [License](#-license)

---

## 🌟 Overview

**Auris** is an enterprise-grade, AI-powered voice bot platform engineered specifically to **replace traditional call centers** in Egypt and the MENA region.

It delivers real-time, ultra-low-latency voice interactions **natively in the Egyptian Arabic dialect**, with a strict architecture built to support **data sovereignty** and **on-premise GPU deployments** — making it the only solution designed from the ground up for the region's regulatory and linguistic requirements.

---

## 🎯 The Problem It Solves

| Challenge | How Auris Solves It |
|---|---|
| 🗣️ **Dialect Barrier** | Global solutions fail with Egyptian Arabic. Auris natively understands and speaks it flawlessly using Whisper V3 + Edge TTS Egyptian voices. |
| 🔒 **Data Sovereignty** | Banks and government entities cannot send data outside Egypt. Auris supports **full on-premise deployment** with local STT & local LLM options. |
| 💸 **Cost & Efficiency** | Reduces call center operational costs by **over 70%** while delivering **24/7 availability** with **zero wait time**. |

---

## 🚀 Core Features

- 📞 **Real-Time Voice Streaming** — Handles inbound calls via Twilio WebSockets with an end-to-end latency of **< 3 seconds**
- 🇪🇬 **Native Egyptian Arabic** — Whisper V3 for local transcription + Edge TTS (`ar-EG-ShakirNeural` / `ar-EG-SalmaNeural`) for natural voice synthesis
- 🤝 **Smart Human Handoff** — Automatically detects unresolvable issues, summarizes call context, and seamlessly transfers to a live agent
- 📊 **Admin Dashboard** — Comprehensive Laravel-based panel for bot configuration, call log monitoring, and real-time analytics
- 🏢 **Enterprise Deployment** — Supports Ollama for fully local LLM inference, enabling air-gapped on-premise setups

---

## 🏗️ System Architecture & Call Flow

```
  ┌─────────────┐     Inbound Call      ┌─────────────────┐
  │   Customer  │ ──────────────────▶  │  Twilio Number  │
  └─────────────┘                       └────────┬────────┘
                                                  │ WebSocket Stream (raw audio)
                                                  ▼
                                        ┌─────────────────┐
                                        │  FastAPI Backend │
                                        │  (Voice Engine)  │
                                        └────────┬────────┘
                                                  │
                          ┌───────────────────────┼───────────────────────┐
                          ▼                       ▼                       ▼
                  ┌──────────────┐      ┌──────────────────┐     ┌──────────────┐
                  │  Whisper V3  │      │  Gemini Flash /  │     │   Edge TTS   │
                  │    (STT)     │ ───▶ │  Ollama (LLM)    │───▶ │    (TTS)     │
                  └──────────────┘      └──────────────────┘     └──────┬───────┘
                                                                         │ Synthesized Audio
                                                                         ▼
                                                               ┌─────────────────┐
                                                               │  Twilio Stream  │
                                                               │  (Back to User) │
                                                               └─────────────────┘
```

### Step-by-Step Flow

1. **Inbound Call** → Customer dials the designated Twilio number
2. **WebSocket Connection** → Twilio triggers a webhook and streams raw audio to the FastAPI backend
3. **STT Processing** → Audio is transcribed in real-time by **Whisper V3**
4. **LLM Engine** → Transcript is processed by **Gemini Flash** to generate a contextual, dialect-accurate response
5. **TTS Synthesis** → Response text is synthesized into speech via **Edge TTS**
6. **Outbound Stream** → Audio streams back via WebSocket to Twilio and is played to the customer

---

## 💻 Tech Stack

| Layer | Technology |
|---|---|
| **Telecom / VoIP** | Twilio (Media Streams & Webhooks) |
| **Backend API (Voice Engine)** | Python — FastAPI, WebSockets |
| **Admin Dashboard** | PHP — Laravel + Blade, MySQL |
| **Speech-to-Text (STT)** | Whisper V3 *(optimized for local RTX 4070 12GB)* |
| **LLM Engine (MVP)** | Google Gemini Flash API |
| **LLM Engine (Enterprise)** | Ollama *(fully local inference)* |
| **Text-to-Speech (TTS)** | Edge TTS (`ar-EG-ShakirNeural`, `ar-EG-SalmaNeural`) |
| **Infrastructure** | Cloudflare Tunnels, Ubuntu |

---

## 📂 Project Structure

```
auris-ai/
│
├── backend/                    # ⚙️  FastAPI Voice Engine
│   ├── main.py                 # Application entry point & WebSocket handlers
│   ├── ai_engine.py            # Whisper, Gemini, and TTS integration
│   ├── twilio_utils.py         # Twilio TwiML and Stream management
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # API keys & config (not committed)
│
├── dashboard/                  # 🖥️  Laravel Admin Panel
│   ├── app/                    # Controllers & Models
│   ├── routes/                 # Web & API routes
│   ├── resources/views/        # Blade templates (UI)
│   ├── composer.json           # PHP dependencies
│   └── .env                    # Database & App config (not committed)
│
└── README.md                   # 📄  Project documentation
```

---

## ⚙️ Environment Variables

> ⚠️ **Never commit `.env` files to version control.** Use `.env.example` as a reference template.

### `backend/.env` — FastAPI Voice Engine

```env
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
GEMINI_API_KEY=your_google_gemini_api_key
PORT=8000
```

### `dashboard/.env` — Laravel Admin Panel

```env
APP_NAME=Auris
APP_ENV=local
APP_KEY=base64:your_generated_app_key
APP_DEBUG=true
APP_URL=http://localhost:8000

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=auris_db
DB_USERNAME=root
DB_PASSWORD=your_secure_password
```

---

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.10+
- PHP 8.1+ & Composer
- MySQL
- Node.js (for Laravel asset compilation)
- NVIDIA GPU with CUDA (for Whisper local inference)
- [Cloudflare Tunnel CLI](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) (`cloudflared`)

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/YourUsername/auris-ai.git
cd auris-ai
```

---

### Step 2 — Run the FastAPI Voice Engine

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# → Edit .env with your API keys

# Start the development server
uvicorn main:app --reload --port 8000
```

---

### Step 3 — Expose Localhost via Cloudflare Tunnel

Twilio requires a **public HTTPS URL** to reach your local server. Use Cloudflare Tunnel:

```bash
cloudflared tunnel --url http://localhost:8000
```

> Copy the generated `https://xxxx.trycloudflare.com` URL.  
> Paste it into: **Twilio Console → Phone Numbers → Active Number → Webhook URL**

---

### Step 4 — Run the Laravel Admin Dashboard

Open a **new terminal window**:

```bash
cd dashboard

# Install PHP dependencies
composer install

# Set up environment
cp .env.example .env
php artisan key:generate
# → Edit .env with your database credentials

# Run database migrations
php artisan migrate

# Start the development server
php artisan serve
```

> Dashboard will be available at: **http://localhost:8000**

---

## 📈 KPIs & Success Metrics

| Metric | Target |
|---|---|
| 🎯 **First Call Resolution (FCR) Rate** | > 70% |
| ⚡ **Average Response Latency** | < 3 seconds |
| 🤝 **Transfer to Human Rate** | < 30% |
| 💰 **Cost Reduction vs. Traditional Call Centers** | > 60% |

---

## 📜 License

**Proprietary & Confidential**

Copyright © 2026 **AISSP**. All Rights Reserved.

This repository and its contents are the proprietary property of AISSP. Unauthorized copying, modification, distribution, or use of this software — via any medium — is strictly prohibited without the express written permission of the author. This software is **not open-source**.

---

<div align="center">

Built with ❤️ for Egypt & the MENA region by **AISSP**

</div>