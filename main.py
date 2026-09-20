
import os
import subprocess
import uuid
from fastapi import (
    FastAPI,
    Request
)
from fastapi.responses import FileResponse
from pydantic import BaseModel

from qa import make_answer
from tts import generate_tts
from stt import transcribe_audio


app = FastAPI(
    title="CLARO V1",
    version="1.0"
)


AUDIO_DIR = "audio"

os.makedirs(AUDIO_DIR, exist_ok=True)


class ChatRequest(BaseModel):
    question: str


# --------------------------------------------------
# FFmpeg
# --------------------------------------------------

def convert_audio(input_file, output_file):

    command = [
        "ffmpeg",
        "-y",
        "-i", input_file,

        # Whisper-friendly format
        "-ar", "16000",
        "-ac", "1",

        output_file
    ]

    subprocess.run(
        command,
        check=True
    )

    return output_file


# --------------------------------------------------
# Basic endpoints
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "device": "CLARO",
        "version": "V1",
        "status": "online"
    }


@app.get("/status")
def status():

    return {
        "device": "CLARO",
        "status": "online"
    }


# --------------------------------------------------
# Text question
# --------------------------------------------------

@app.post("/chat")
def chat(request: ChatRequest):

    question = request.question.strip()

    if not question:

        return {
            "answer": "Please ask me a question."
        }

    answer = make_answer(question)

    audio_file = generate_tts(answer)

    return {
        "question": question,
        "answer": answer,
        "audio": audio_file
    }


# --------------------------------------------------
# ESP32 audio upload
# --------------------------------------------------

@app.post("/upload-audio")
async def upload_audio(request: Request):

    incoming_file = os.path.join(
        AUDIO_DIR,
        "incoming.wav"
    )

    converted_file = os.path.join(
        AUDIO_DIR,
        "converted.wav"
    )

    print()
    print("================================")
    print("CLARO AUDIO REQUEST")
    print("================================")

    # --------------------------------------------------
    # Receive audio
    # --------------------------------------------------

    data = await request.body()

    print(
        f"Received: {len(data)} bytes"
    )

    if not data:
        return {
            "question": "",
            "answer": ""
        }

    # --------------------------------------------------
    # Save incoming WAV
    # --------------------------------------------------

    with open(
        incoming_file,
        "wb"
    ) as audio:

        audio.write(data)

    print(
        "Audio saved."
    )

    # --------------------------------------------------
    # Convert with FFmpeg
    # --------------------------------------------------

    try:

        convert_audio(
            incoming_file,
            converted_file
        )

        print(
            "FFmpeg conversion complete."
        )

    except Exception as error:

        print(
            f"FFmpeg error: {error}"
        )

        return {
            "question": "",
            "answer": ""
        }

    # --------------------------------------------------
    # Speech to text
    # --------------------------------------------------

    question = transcribe_audio(
        converted_file
    )

    question = question.strip()

    print(
        f"User: {question}"
    )

    # --------------------------------------------------
    # NO SPEECH
    # --------------------------------------------------

    if not question:

        print(
            "No speech detected."
        )

        # Delete temporary files

        for file in [
            incoming_file,
            converted_file
        ]:

            if os.path.exists(file):

                os.remove(file)

        return {
            "question": "",
            "answer": ""
        }

    # --------------------------------------------------
    # QUESTION RECEIVED
    # --------------------------------------------------

    answer = make_answer(
        question
    )

    print(
        f"CLARO: {answer}"
    )

    # --------------------------------------------------
    # TTS
    # --------------------------------------------------

    response_file = generate_tts(
        answer
    )

    print(
        f"Response: {response_file}"
    )

    # --------------------------------------------------
    # Clean temporary input files
    # --------------------------------------------------

    for file in [
        incoming_file,
        converted_file
    ]:

        if os.path.exists(file):

            try:

                os.remove(file)

            except Exception as error:

                print(
                    f"Could not delete {file}: {error}"
                )

    print(
        "Temporary files cleaned."
    )

    print(
        "================================"
    )

    return {
        "question": question,
        "answer": answer
    }
@app.get("/audio")
def get_audio():

    response_file = os.path.join(
        AUDIO_DIR,
        "response.wav"
    )

    if not os.path.exists(response_file):

        return {
            "error": "No response audio available."
        }

    return FileResponse(
        response_file,
        media_type="audio/wav",
        filename="response.wav"
    )
