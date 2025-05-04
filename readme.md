# 🎙️ YouTube Transcription & Chat Agent

A fast, offline-friendly **proof of concept (POC)** to transcribe YouTube videos and chat with the content using a local LLM via [Ollama](https://ollama.com/). Built with Flask, Whisper, PostgreSQL, and Mistral.

---

## ✅ Features

- 🧠 Transcribe YouTube audio using Whisper for Transcribe operation and Mistral Model for Chat
- 💬 Chat with transcript using **Ollama** (Mistral, LLaMA2, etc.)
- 📦 Local PostgreSQL-backed storage
- ⚙️ Configurable via `.env`

---

## 🔧 Prerequisites

- Python 3.10+
- Docker
- Ollama with mistral:7b-instruct-fp16 model

---

## 🚀 Getting Started

### 1. Clone the Project

```bash
git clone https://github.com/13shivam/yt-transcribe-chat-agent.git
cd yt-transcribe-chat-agent
````

### 2. Make sure a .env File exists
```bash
FLASK_APP=app.py
FLASK_ENV=development

# Ollama setup
OLLAMA_MODEL=mistral:7b-instruct-fp16
OLLAMA_API=http://localhost:11434/api/chat

# PostgreSQL connection
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ytagent
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgers

# Whisper model
WHISPER_MODEL=base
```

### 3. Run Local Ollama with Mistral Model (7b-instruct-fp16 - 14gb)
```bash
brew install ollama
ollama run mistral:7b-instruct-fp16
```
### 4. Run App
```bash
docker compose build --no-cache
docker compose up -d
```
![My Local Image](resource/docker_run.png)

### Access APIs via Swagger
http://127.0.0.1:5050/apidocs/#

### Sequence Diagram all APIs 
![My Local Image](resource/ytagent.png)

### Swagger API Local Demo
![My Local Image](resource/swaggerpreview.png)

### Step 1: Upload API youtube URL
![My Local Image](resource/upload_api_demo.png)

### Step 2: Check JobStatus
![My Local Image](resource/job_status_poll_api.png)

### Step 3: Initiate Chat from JobId
![My Local Image](resource/swagger_job_api_chat.png)

### Misc Screenshots
1. DB Screenshots
![in_progress_statu.png](resource/in_progress_statu.png)
![db_transcript_complete_status.png](resource/db_transcript_complete_status.png)
2. Chat API preview
![chat_interface_job_id.png](resource/chat_interface_job_id.png)
3. Flask App Logs
![flask_app_logs.png](resource/flask_logs_startup.png)

### 🪪 WIP to add in future release: 
- Speaker Diarization support via open source `pyannote.audio` 