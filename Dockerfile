FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    ffmpeg \
    python3-dev \
    libffi-dev \
    libsndfile1 \
    && apt-get clean && apt install -y curl

RUN pip install --upgrade pip
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir --upgrade yt-dlp


COPY . /app

EXPOSE 5050

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0", "--port=5050"]
