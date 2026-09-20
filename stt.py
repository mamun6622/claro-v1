from faster_whisper import WhisperModel

print("Loading STT model...")

model = WhisperModel(
    "tiny",
    device="cpu",
    compute_type="int8"
)

print("STT model loaded.")


def transcribe_audio(audio_file):

    segments, info = model.transcribe(
        audio_file,
        language="en",
        beam_size=1,
        vad_filter=True,
        vad_parameters={
            "min_silence_duration_ms": 500
        }
    )

    texts = []

    for segment in segments:

        # Ignore very low-confidence speech
        if segment.no_speech_prob > 0.6:
            continue

        text = segment.text.strip()

        if text:
            texts.append(text)

    result = " ".join(texts).strip()

    return result