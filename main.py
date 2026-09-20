import os
import subprocess

from fastapi import (
    FastAPI,
    Request
)

from fastapi.responses import FileResponse

from pydantic import BaseModel

from qa import make_answer

from tts import generate_tts

from stt import transcribe_audio


# ============================================================
# CLARO V1
# BACKEND
# ============================================================

app = FastAPI(
    title="CLARO V1",
    version="1.0"
)


# ============================================================
# AUDIO DIRECTORY
# ============================================================

AUDIO_DIR = "audio"

os.makedirs(
    AUDIO_DIR,
    exist_ok=True
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):

    question: str


# ============================================================
# FFMPEG AUDIO CONVERSION
# ============================================================

def convert_audio(
    input_file,
    output_file
):

    command = [

        "ffmpeg",

        "-y",

        "-i",
        input_file,

        "-ar",
        "16000",

        "-ac",
        "1",

        output_file
    ]


    subprocess.run(
        command,
        check=True
    )


    return output_file


# ============================================================
# BASIC ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {

        "device": "CLARO",

        "version": "V1",

        "status": "online"
    }


# ============================================================
# STATUS
# ============================================================

@app.get("/status")
def status():

    return {

        "device": "CLARO",

        "status": "online"
    }


# ============================================================
# TEXT CHAT
# ============================================================

@app.post("/chat")
def chat(
    request: ChatRequest
):

    question = request.question.strip()


    if not question:

        return {

            "question": "",

            "answer": ""
        }


    answer = make_answer(
        question
    )


    print()
    print(
        f"User: {question}"
    )

    print(
        f"CLARO: {answer}"
    )


    # --------------------------------------------------------
    # Generate TTS
    # --------------------------------------------------------

    audio_file = generate_tts(
        answer
    )


    return {

        "question": question,

        "answer": answer,

        "audio": audio_file
    }


# ============================================================
# ESP32 AUDIO UPLOAD
# ============================================================

@app.post("/upload-audio")
async def upload_audio(
    request: Request
):


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


    # ========================================================
    # RECEIVE AUDIO
    # ========================================================

    data = await request.body()


    print(
        f"Received: {len(data)} bytes"
    )


    if not data:

        print(
            "No audio received."
        )

        return {

            "question": "",

            "answer": ""
        }


    # ========================================================
    # SAVE INCOMING WAV
    # ========================================================

    try:

        with open(
            incoming_file,
            "wb"
        ) as audio:

            audio.write(data)


        print(
            "Audio saved."
        )


    except Exception as error:

        print(
            f"Audio save error: {error}"
        )

        return {

            "question": "",

            "answer": ""
        }


    # ========================================================
    # FFMPEG CONVERSION
    # ========================================================

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


        # Cleanup

        for file in [

            incoming_file,

            converted_file

        ]:

            if os.path.exists(file):

                try:

                    os.remove(file)

                except:

                    pass


        return {

            "question": "",

            "answer": ""
        }


    # ========================================================
    # SPEECH TO TEXT
    # ========================================================

    question = transcribe_audio(

        converted_file
    )


    question = question.strip()


    # ========================================================
    # NO SPEECH
    # ========================================================

    if not question:

        print()
        print(
            "User: no speech"
        )

        print(
            "CLARO: silent"
        )


        # ----------------------------------------------------
        # IMPORTANT:
        #
        # DO NOT:
        # - call make_answer()
        # - call generate_tts()
        # - create new response.wav
        #
        # The previous response.wav must remain irrelevant.
        # The ESP32 will NOT download it.
        # ----------------------------------------------------


        # Cleanup

        for file in [

            incoming_file,

            converted_file

        ]:

            if os.path.exists(file):

                try:

                    os.remove(file)

                except Exception as error:

                    print(
                        f"Cleanup error: {error}"
                    )


        print(
            "Nothing to answer."
        )

        print("================================")


        return {

            "question": "",

            "answer": ""
        }


    # ========================================================
    # REAL QUESTION
    # ========================================================

    print()
    print(
        f"User: {question}"
    )


    # ========================================================
    # ANSWER
    # ========================================================

    try:

        answer = make_answer(
            question
        )


    except Exception as error:

        print(
            f"QA error: {error}"
        )


        answer = (
            "Sorry, I couldn't find "
            "that information."
        )


    print(
        f"CLARO: {answer}"
    )


    # ========================================================
    # TTS
    # ========================================================

    try:

        response_file = generate_tts(
            answer
        )


        print(
            f"Response: {response_file}"
        )


    except Exception as error:

        print(
            f"TTS error: {error}"
        )


        # Cleanup

        for file in [

            incoming_file,

            converted_file

        ]:

            if os.path.exists(file):

                try:

                    os.remove(file)

                except:

                    pass


        return {

            "question": question,

            "answer": answer
        }


    # ========================================================
    # CLEAN TEMPORARY FILES
    # ========================================================

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


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "question": question,

        "answer": answer
    }


# ============================================================
# AUDIO DOWNLOAD
# ============================================================

@app.get("/audio")
def get_audio():

    response_file = os.path.join(

        AUDIO_DIR,

        "response.wav"
    )


    if not os.path.exists(
        response_file
    ):

        return {

            "error":
            "No response audio available."
        }


    return FileResponse(

        response_file,

        media_type="audio/wav",

        filename="response.wav"
    )