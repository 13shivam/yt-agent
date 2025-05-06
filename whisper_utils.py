
import os

import whisper
import yt_dlp as youtube_dl

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

model = whisper.load_model(WHISPER_MODEL)

def download_audio_from_youtube(youtube_url: str, out_path: str = "downloads"):
    os.makedirs(out_path, exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(out_path, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'verbose': True,
    }


    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        filename = os.path.join(out_path, f"{info['id']}.mp3")
        return filename, info['title'], info['id']

def transcribe_audio(audio_path: str):
    result = model.transcribe(audio_path)
    return result["text"]


def chunk_transcript(transcript, max_token_limit=6000, overlap=1):
    """
    Split the transcript into chunks, with a sliding window to maintain context continuity.
    """
    chunks = []
    for i in range(0, len(transcript), max_token_limit - overlap):
        chunk = transcript[i:i + max_token_limit]
        chunks.append(chunk)
    return chunks
