from faster_whisper import WhisperModel
import os
import wave
from array import array
import math
import sys


print("Loading STT model...")

model = WhisperModel(
    "tiny",
    device="cpu",
    compute_type="int8"
)

print("STT model loaded.")


def has_speech(audio_file, threshold=300):
    """
    Check whether the WAV file contains enough audio energy
    to likely contain speech.
    """

    try:
        with wave.open(audio_file, "rb") as wav:

            frames = wav.readframes(wav.getnframes())

            if not frames:
                return False

            sample_width = wav.getsampwidth()

            # We expect 16-bit PCM after FFmpeg conversion
            if sample_width != 2:
                print(f"Unexpected sample width: {sample_width}")
                return False

            samples = array("h")
            samples.frombytes(frames)

            if not samples:
                return False

            # WAV PCM is little-endian
            if sys.byteorder != "little":
                samples.byteswap()

            # RMS = average signal energy
            rms = math.sqrt(
                sum(sample * sample for sample in samples)
                / len(samples)
            )

            print(f"Audio RMS: {rms:.2f}")

            if rms > threshold:
                return True

            return False

    except Exception as error:
        print(f"Audio level check error: {error}")
        return False


def transcribe_audio(audio_file):

    if not os.path.exists(audio_file):
        print("STT file does not exist.")
        return ""

    # --------------------------------
    # STEP 1: Check for actual audio
    # --------------------------------

    if not has_speech(audio_file):
        print("Audio is silent.")
        print("Skipping Whisper.")
        return ""

    print("Speech detected.")
    print("Running Whisper...")

    # --------------------------------
    # STEP 2: Whisper transcription
    # --------------------------------

    try:

        segments, info = model.transcribe(
            audio_file,
            language="en",
            beam_size=1,
            temperature=0,
            vad_filter=True,
            vad_parameters={
                "min_silence_duration_ms": 500
            }
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
        ).strip()

        print(f"Whisper result: {text}")

        return text

    except Exception as error:

        print(f"Whisper error: {error}")

        return ""