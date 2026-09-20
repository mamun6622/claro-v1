
import os
import subprocess
import pyttsx3


AUDIO_DIR = "audio"

RAW_FILE = os.path.join(
    AUDIO_DIR,
    "tts_raw.wav"
)

OUTPUT_FILE = os.path.join(
    AUDIO_DIR,
    "response.wav"
)


def generate_tts(text):

    os.makedirs(
        AUDIO_DIR,
        exist_ok=True
    )

    engine = pyttsx3.init()

    engine.setProperty(
        "rate",
        175
    )

    engine.save_to_file(
        text,
        RAW_FILE
    )

    engine.runAndWait()

    engine.stop()

    if not os.path.exists(RAW_FILE):

        raise RuntimeError(
            "TTS file was not created."
        )

    # FFmpeg converts the TTS output
    # into a format suitable for ESP32.
    command = [
        "ffmpeg",
        "-y",

        "-i",
        RAW_FILE,

        "-ar",
        "16000",

        "-ac",
        "1",

        OUTPUT_FILE
    ]

    subprocess.run(
        command,
        check=True
    )

    return OUTPUT_FILE
