import json
import logging
import os
import uuid
from threading import Thread

import requests
from dotenv import load_dotenv
from flasgger import Swagger, swag_from
from flask import Flask, request, jsonify

from db import DatabaseService
from swagger_specs import submit_url_spec, status_spec, chat_spec
from whisper_utils import download_audio_from_youtube, transcribe_audio, chunk_transcript
from yt_utils import extract_video_id

app = Flask(__name__)
swagger = Swagger(app)
load_dotenv()
OLLAMA_API = os.getenv("OLLAMA_API")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
logging.basicConfig(level=logging.DEBUG)
db = DatabaseService()


def background_process(job_id, url, video_id):
    try:
        db.save_or_update_transcript(video_id, status="INIT")
        # Downloading audio from YouTube
        audio_file, title, video_id = download_audio_from_youtube(url)
        db.save_or_update_transcript(video_id, status="IN_PROGRESS")
        # Transcribing audio to text
        transcript = transcribe_audio(audio_file)
        db.save_or_update_transcript(video_id, transcript=transcript, status="COMPLETE")
        db.create_or_update_context(job_id, video_id, None)
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.route("/submit", methods=["POST"])
@swag_from(submit_url_spec)
def submit_url():
    url = request.json["youtube_url"]
    job_id = str(uuid.uuid4())  # Generate a unique job ID
    video_id = extract_video_id(url)
    transcript, status = db.fetch_transcript_status(video_id)
    if transcript is None and (status != "INIT" or status != "IN_PROGRESS"):
        Thread(target=background_process, args=(job_id, url, video_id)).start()
    else:
        db.create_or_update_context(job_id, video_id, None)
    return jsonify({"job_id": job_id})


@app.route("/status/<job_id>")
@swag_from(status_spec)
def get_status(job_id):
    """Poll this endpoint for the current status of the job"""
    #video_id = db.fetch_video_details(job_id)
    return jsonify(db.fetch_status_by_job_id(job_id))


@app.route("/chat", methods=["POST"])
@swag_from(chat_spec)
def chat():
    user_msg = request.json["message"]
    job_id = request.json["job_id"]

    video_id = db.fetch_video_details(job_id)
    transcript, status = db.fetch_transcript_status(video_id)

    if not transcript:
        return jsonify({"reply": "Sorry, the video transcripting is still processing."})

    chunks = chunk_transcript(transcript)
    final_response = process_chunks(chunks, user_msg)
    db.create_or_update_context(job_id, video_id, final_response)
    return {"reply": final_response}


def call_ollama_api_and_parse_response(system_prompt, user_msg):
    """
    Makes a request to the OLLAMA API with the given system prompt and user message,
    and returns the parsed response content.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ]
    }

    response = requests.post(OLLAMA_API, json=payload)

    if response.status_code == 200:
        try:
            response_lines = response.text.splitlines()
            parsed_responses = [json.loads(line) for line in response_lines]

            combined_message = " ".join([
                str(resp.get('message', {}).get('content', ''))
                for resp in parsed_responses
            ])

            return combined_message
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return f"Error parsing JSON: {e}"
    else:
        print(f"API error. Status Code: {response.status_code}")
        return f"Error. Status Code: {response.status_code}"


def process_chunks(chunks, user_msg):
    full_response = ""

    for i, chunk in enumerate(chunks):
        system_prompt = f"""
        You are a helpful assistant who answers questions based on the following transcript. Be attentive and answer based on the provided context. Here's the transcript:
        {chunk}
        """

        result = call_ollama_api_and_parse_response(system_prompt, user_msg)
        full_response += result

    # Finally combine all the multi chunk response to give formatted reply
    compact_response = call_ollama_api_and_parse_response(full_response, user_msg)

    return compact_response


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5050)
