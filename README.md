
# CLARO  —  Campus Companion Robot

<img width="240" height="320" alt="IMG_4975" src="https://github.com/user-attachments/assets/1e32a0de-d698-4adb-b642-e95bc032f459" />
<img width="240" height="320" alt="IMG_4976" src="https://github.com/user-attachments/assets/a6f01657-f0c8-4fad-81c3-da19848f1baf" />
<img width="240" height="320" alt="IMG_4984" src="https://github.com/user-attachments/assets/8f22bb07-5ab1-465d-83cd-8e9b3b556b49" />
<img width="240" height="320" alt="IMG_4991" src="https://github.com/user-attachments/assets/fa317c7a-fd50-4fbc-b74e-e509c7af9725" />

CLARO is a voice-based campus assistant built with an **ESP32-S3** and a local **Python/FastAPI** backend. It answers campus questions from a local JSON knowledge base and provides animated facial expressions on its TFT display.

## Features

- Voice input with INMP441 microphone
- Local speech recognition with Faster-Whisper
- Campus Q&A using a local JSON database
- Spoken responses using pyttsx3 and FFmpeg
- 2.0-inch TFT animated face with idle, listening, thinking, speaking and error states
- Servo-based left/right head scanning
- Wi-Fi communication between ESP32-S3 and PC

## System

```text
INMP441 → ESP32-S3 → Wi-Fi → FastAPI backend
                              ├─ Faster-Whisper
                              ├─ sqlite Q&A
                              └─ pyttsx3 + FFmpeg
MAX98357A + Speaker ← ESP32-S3 ← Response audio

ESP32-S3 → ST7789 TFT display
ESP32-S3 → Pan servo
```

The ESP32-S3 manages the microphone, speaker, display and servo. The PC handles speech recognition, campus information search and speech generation.

## Hardware

- ESP32-S3
- INMP441 I2S microphone
- MAX98357A I2S amplifier and speaker
- 2.0-inch ST7789 SPI TFT (320 × 240 landscape)
- Pan servo
- PC running the backend

## Wiring

| Component | Signal | ESP32-S3 |
|---|---|---:|
| INMP441 | BCLK / SCK | GPIO 4 |
| INMP441 | WS / LRC | GPIO 5 |
| INMP441 | SD | GPIO 6 |
| MAX98357A | BCLK | GPIO 4 |
| MAX98357A | LRC | GPIO 5 |
| MAX98357A | DIN | GPIO 18 |
| MAX98357A | SD / MODE | GPIO 17 |
| ST7789 | CS | GPIO 10 |
| ST7789 | DC | GPIO 13 |
| ST7789 | RST | GPIO 14 |
| ST7789 | MOSI / SDA | GPIO 11 |
| ST7789 | SCLK / SCL | GPIO 12 |
| Pan servo | Signal | GPIO 7 |

**Power:** INMP441 and TFT use 3.3V. MAX98357A uses 5V. Connect grounds together. Power the servo from a suitable supply for the servo and connect its ground to ESP32-S3 GND.

## Servo Behaviour

The servo scans gradually between approximately 70° and 110° while CLARO is idle or listening. It returns to the center position while CLARO is thinking, speaking or showing an error.

## Software

- Python, FastAPI and Uvicorn
- Faster-Whisper (`tiny`)
- pyttsx3
- FFmpeg
- Arduino IDE
- Adafruit GFX, Adafruit ST7789 and ESP32Servo libraries

## Setup

```powershell
git clone https://github.com/mamun6622/claro-v1.git
cd claro-v1

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install FFmpeg and confirm `ffmpeg -version` works.

## Run

Start the backend:

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

Set your Wi-Fi credentials and PC backend IP in `esp32/claro_esp32.ino`, then upload the firmware. The ESP32-S3 and PC must be on the same network.

Backend status: `http://127.0.0.1:8001/status`

## Project Structure

```text
claro-v1/
├── main.py
├── scraper.py
├── qa.py
├── stt.py
├── tts.py
├── claro.db
├── database/
│   └── bic_knowledge.json
├── audio/
└── esp32/
    └── claro_esp32.ino
```

## Current Scope

CLARO V1 uses local keyword-based campus search rather than an LLM or vector database. Speech processing runs on the PC; the ESP32-S3 controls the physical interface.

**Project lead:** Mamun

**Member 2 :** Siam

**Member 3:** Ayush

**Institution:** Tongmyong University, Busan, South Korea
