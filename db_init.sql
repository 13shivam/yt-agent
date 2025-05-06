--CREATE DATABASE ytagent;
--CREATE USER IF NOT EXISTS postgres WITH ENCRYPTED PASSWORD 'postgres';
--GRANT ALL PRIVILEGES ON DATABASE ytagent TO postgres;

CREATE TABLE video_transcript_mapping (
    id SERIAL PRIMARY KEY,
  	video_id VARCHAR UNIQUE NOT NULL,
   status VARCHAR,
    transcript TEXT NULL
);

CREATE TABLE job_chat_context (
    id SERIAL PRIMARY KEY,
    job_id TEXT UNIQUE NOT NULL,
    context JSONB NULL,
  video_id VARCHAR
);





