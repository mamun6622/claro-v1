# CLARO V1 — Your Intelligent Campus Companion

CLARO is a campus assistant robot designed to help students and visitors interact with university information through **voice-based questions and spoken responses**.

The V1 prototype uses an **ESP32-S3**, **INMP441 microphone**, **MAX98357A audio amplifier**, and speaker, while the heavier processing runs on a PC.

> **CLARO V1 focuses on a simple, reliable architecture rather than heavy AI.**
>
> Voice → Speech-to-Text → Local Knowledge Search → Text-to-Speech → Speaker

---

## ✨ Features

* 🎤 Voice input through INMP441 I2S microphone
* 🧠 Local campus knowledge database
* 🔎 Simple keyword-based question answering
* 🗣️ Speech-to-text using Faster-Whisper
* 🔊 Text-to-speech using pyttsx3
* 🎵 Audio conversion using FFmpeg
* 📡 Wi-Fi communication between ESP32 and PC
* 🔈 Audio playback through MAX98357A
* 👋 Built-in conversational greetings
* 🤖 CLARO identity and capability responses
* 🌐 FastAPI backend
* 💾 Local JSON knowledge storage
* 🔄 Automatic continuous listening

---

# 🏗️ System Architecture

```text
                  ┌──────────────────────┐
                  │      CLARO V1        │
                  │      ESP32-S3        │
                  └──────────┬───────────┘
                             │
                             │ I2S
                             ▼
                    ┌─────────────────┐
                    │    INMP441      │
                    │   Microphone    │
                    └────────┬────────┘
                             │
                             │ WAV
                             ▼
                    ┌─────────────────┐
                    │      Wi-Fi      │
                    └────────┬────────┘
                             │
                             │ HTTP POST
                             ▼
              ┌──────────────────────────────┐
              │          PC Backend          │
              │                              │
              │          FastAPI             │
              │             │                │
              │          FFmpeg              │
              │             │                │
              │       Faster-Whisper         │
              │             │                │
              │          qa.py               │
              │             │                │
              │     bic_knowledge.json      │
              │             │                │
              │          pyttsx3             │
              │             │                │
              │          FFmpeg              │
              └──────────────┬───────────────┘
                             │
                             │ HTTP GET
                             ▼
                    ┌─────────────────┐
                    │     ESP32-S3    │
                    └────────┬────────┘
                             │
                             │ I2S
                             ▼
                    ┌─────────────────┐
                    │    MAX98357A    │
                    │ Amplifier       │
                    └────────┬────────┘
                             │
                             ▼
                         🔊 Speaker
```

---

# 🔄 Voice Pipeline

When a user speaks to CLARO:

```text
1. ESP32 records audio
        ↓
2. WAV audio is created
        ↓
3. ESP32 uploads WAV to PC
        ↓
4. FastAPI receives audio
        ↓
5. FFmpeg converts audio
        ↓
6. Faster-Whisper converts speech → text
        ↓
7. CLARO searches local knowledge database
        ↓
8. Answer is generated
        ↓
9. pyttsx3 converts text → speech
        ↓
10. FFmpeg prepares final WAV
        ↓
11. ESP32 downloads response
        ↓
12. MAX98357A plays audio
```

---

# 📁 Project Structure

```text
CLARO-V1/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── main.py
├── scraper.py
├── qa.py
├── stt.py
├── tts.py
│
├── database/
│   └── bic_knowledge.json
│
├── audio/
│   └── .gitkeep
│
└── esp32/
    └── claro_esp32.ino
```

### Main files

| File                 | Purpose                               |
| -------------------- | ------------------------------------- |
| `main.py`            | FastAPI backend and audio API         |
| `scraper.py`         | Downloads university information      |
| `qa.py`              | Searches the local knowledge database |
| `stt.py`             | Speech-to-text using Faster-Whisper   |
| `tts.py`             | Text-to-speech and FFmpeg processing  |
| `bic_knowledge.json` | Local campus knowledge                |
| `claro_esp32.ino`    | ESP32 firmware                        |

---

# 💻 PC Requirements

## Hardware

Recommended:

* Windows 10/11
* Python 3.11+
* 8 GB RAM minimum
* Internet connection
* NVIDIA GPU is optional

A GPU can improve speech recognition performance, but CLARO V1 is designed to work without one.

---

# 🧰 Software Requirements

Install:

* Python
* Git
* FFmpeg
* Arduino IDE
* ESP32 Arduino board support

---

# 🐍 Python Setup

Clone the repository:

```bash
git clone https://github.com/mamun6622/claro-v1.git
```

Enter the project:

```bash
cd claro-v1
```

Create a virtual environment:

### Windows PowerShell

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

You should see:

```text
(.venv)
```

at the beginning of your terminal.

---

# 📦 Install Python Dependencies

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install project dependencies:

```powershell
python -m pip install -r requirements.txt
```

The main Python packages include:

```text
fastapi
uvicorn
requests
beautifulsoup4
pyttsx3
faster-whisper
python-multipart
```

---

# 🎵 FFmpeg Setup

CLARO uses FFmpeg for audio conversion.

Verify that FFmpeg is installed:

```powershell
ffmpeg -version
```

If the command works, FFmpeg is ready.

The Python application expects the `ffmpeg` command to be available through the system PATH.

---

# 🗄️ Campus Knowledge Database

CLARO uses a local JSON database instead of a vector database or external AI service.

The database is located at:

```text
database/bic_knowledge.json
```

The scraper collects information from configured university pages.

Run:

```powershell
python scraper.py
```

The collected information is stored locally in:

```text
database/bic_knowledge.json
```

### Adding new websites

Open:

```text
scraper.py
```

Find:

```python
SOURCES = [
    "https://www.tu.ac.kr/ic/index.do",
]
```

Add additional trusted university pages:

```python
SOURCES = [
    "https://www.tu.ac.kr/ic/index.do",
    "YOUR_ADDITIONAL_URL",
]
```

Then run:

```powershell
python scraper.py
```

---

# 🤖 ESP32 Hardware

## Required Components

### Main controller

* ESP32-S3

### Audio input

* INMP441 I2S microphone

### Audio output

* MAX98357A I2S amplifier
* Speaker

### Additional components

* USB cable
* Jumper wires
* 5V power source
* Wi-Fi network

---

# 🔌 Wiring

## INMP441 → ESP32-S3

| INMP441    | ESP32-S3 |
| ---------- | -------- |
| VDD        | 3.3V     |
| GND        | GND      |
| SCK / BCLK | GPIO 4   |
| WS / LRC   | GPIO 5   |
| SD         | GPIO 6   |
| L/R        | GND      |

---

## MAX98357A → ESP32-S3

| MAX98357A | ESP32-S3 |
| --------- | -------- |
| VIN       | 5V       |
| GND       | GND      |
| BCLK      | GPIO 4   |
| LRC       | GPIO 5   |
| DIN       | GPIO 18  |

Connect the speaker to the MAX98357A speaker output.

### Important

The microphone and speaker share the clock lines:

```text
GPIO 4 → BCLK
GPIO 5 → WS/LRC
```

but use different data pins:

```text
GPIO 6  → microphone data
GPIO 18 → speaker data
```

---

# 📡 Configure Wi-Fi

Open:

```text
esp32/claro_esp32.ino
```

Find:

```cpp
const char* WIFI_SSID = "YOUR_WIFI";
const char* WIFI_PASSWORD = "YOUR_PASSWORD";
```

Replace them with your Wi-Fi credentials.

---

# 🖥️ Configure the PC IP Address

The ESP32 communicates with the PC through the local network.

Find your PC's local IP:

```powershell
ipconfig
```

Look for:

```text
IPv4 Address
```

For example:

```text
192.168.1.50
```

Then configure the ESP32:

```cpp
const char* BACKEND_URL =
    "http://192.168.1.50:8001";
```

### Important

The PC and ESP32 must be connected to the **same local network**.

Do not use:

```text
localhost
```

or:

```text
127.0.0.1
```

in the ESP32 firmware.

---

# 🛡️ Keep Credentials Private

Do **not** commit real Wi-Fi credentials to GitHub.

Avoid:

```cpp
const char* WIFI_PASSWORD = "my-real-password";
```

in a public repository.

Instead, keep your local credentials private or use a separate configuration file that is excluded through `.gitignore`.

---

# 🚀 Start the Backend

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start FastAPI:

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

You should see:

```text
Uvicorn running on http://0.0.0.0:8001
```

---

# 🔍 Test the Backend

On the PC, open:

```text
http://127.0.0.1:8001
```

Expected response:

```json
{
    "device": "CLARO",
    "version": "V1",
    "status": "online"
}
```

You can also test:

```text
http://127.0.0.1:8001/status
```

Expected:

```json
{
    "device": "CLARO",
    "status": "online"
}
```

---

# 🔧 Upload ESP32 Firmware

Open:

```text
esp32/claro_esp32.ino
```

in Arduino IDE.

Select your ESP32-S3 board.

Configure the correct COM port.

Then click:

```text
Upload
```

Open Serial Monitor.

The ESP32 should connect to Wi-Fi and communicate with the backend.

---

# 🎤 Using CLARO

After the ESP32 starts:

```text
RECORDING

Speak now...
```

Speak a question.

For example:

```text
Hi Claro
```

CLARO responds with a greeting.

Example:

```text
Hello! I'm CLARO, your intelligent campus companion.
How can I help you today?
```

You can also ask:

```text
Who are you?
```

or:

```text
What can you do?
```

For campus questions:

```text
Where is BIC?
```

```text
What programs are available?
```

```text
Tell me about admission.
```

The answer is retrieved from the local campus knowledge database.

---

# 🌐 Backend API

## GET `/`

Returns basic CLARO information.

Example:

```http
GET /
```

Response:

```json
{
    "device": "CLARO",
    "version": "V1",
    "status": "online"
}
```

---

## GET `/status`

Checks backend status.

```http
GET /status
```

Response:

```json
{
    "device": "CLARO",
    "status": "online"
}
```

---

## POST `/chat`

Accepts a text question.

Example:

```json
{
    "question": "Who are you?"
}
```

Returns:

```json
{
    "question": "Who are you?",
    "answer": "I'm CLARO, your intelligent campus companion..."
}
```

---

## POST `/upload-audio`

The ESP32 sends recorded WAV audio to this endpoint.

```http
POST /upload-audio
Content-Type: audio/wav
```

The backend:

1. Receives the audio
2. Converts it using FFmpeg
3. Transcribes it
4. Searches the campus database
5. Generates an answer
6. Generates TTS audio

---

## GET `/audio`

Returns the latest generated response audio.

```http
GET /audio
```

The ESP32 downloads this file and plays it through the MAX98357A.

---

# 🧠 Question Answering

CLARO V1 intentionally uses a lightweight approach.

It does **not** require:

* Ollama
* Qwen
* OpenAI API
* Vector database
* Embeddings
* RAG framework
* Cloud AI services

Instead:

```text
User Question
      ↓
Keyword Extraction
      ↓
Local JSON Search
      ↓
Matching Information
      ↓
Answer
```

This keeps the V1 architecture simple and easier to debug.

---

# 🗣️ Speech Recognition

CLARO uses:

**Faster-Whisper**

The current configuration uses the:

```text
tiny
```

model.

This provides a lightweight local speech-recognition solution.

The model is loaded when the backend starts rather than being loaded for every request.

---

# 🔊 Text-to-Speech

CLARO V1 uses:

**pyttsx3**

The generated speech is then processed using FFmpeg.

```text
Text
 ↓
pyttsx3
 ↓
Raw WAV
 ↓
FFmpeg
 ↓
16 kHz Mono WAV
 ↓
ESP32
```

---

# 🧹 Temporary Audio Files

Audio files generated during operation are temporary.

Examples:

```text
audio/incoming.wav
audio/converted.wav
audio/tts_raw.wav
audio/response.wav
```

These should not be committed to GitHub.

They are ignored through `.gitignore`.

---

# 🐛 Troubleshooting

## ESP32 cannot connect to backend

Check:

```text
1. PC and ESP32 are on the same Wi-Fi.
2. BACKEND_URL contains the correct PC IP.
3. FastAPI is running.
4. Port 8001 is accessible through Windows Firewall.
```

Test the PC backend:

```powershell
ipconfig
```

Then from another device on the same network, open:

```text
http://YOUR_PC_IP:8001/status
```

---

## `ffmpeg` command not found

Run:

```powershell
ffmpeg -version
```

If Windows cannot find FFmpeg, install FFmpeg and add its `bin` directory to the Windows PATH.

Restart PowerShell after modifying PATH.

---

## Python module not found

Make sure the virtual environment is active:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then:

```powershell
python -m pip install -r requirements.txt
```

---

## Microphone records silence

Check the INMP441 wiring:

```text
BCLK → GPIO 4
WS   → GPIO 5
SD   → GPIO 6
L/R  → GND
```

Also verify:

```text
VDD → 3.3V
GND → GND
```

---

## Speaker produces no sound

Check:

```text
MAX98357A VIN  → 5V
MAX98357A GND  → GND
MAX98357A BCLK → GPIO 4
MAX98357A LRC  → GPIO 5
MAX98357A DIN  → GPIO 18
```

Make sure the speaker is connected to the MAX98357A output.

---

## ESP32 records but CLARO does not answer

Check the FastAPI terminal.

You should see:

```text
CLARO AUDIO REQUEST
```

followed by:

```text
Received: XXXXX bytes
Audio saved.
FFmpeg conversion complete.
User: ...
CLARO: ...
```

If the request never reaches FastAPI, check the Wi-Fi connection and IP address.

---

# 🔐 Security Notes

CLARO V1 is designed primarily for local development and prototyping.

The FastAPI server currently does not provide production-grade authentication.

Do not expose the backend directly to the public internet.

For a production deployment, consider adding:

* Authentication
* HTTPS
* API keys
* Input validation
* Rate limiting
* Secure configuration
* Network isolation

---

# 🚧 Current V1 Limitations

CLARO V1 intentionally has a limited scope.

Current version does not include:

* Face recognition
* Emotion recognition
* Autonomous navigation
* Large language model reasoning
* Cloud AI
* Vector search
* Long-term user memory
* Advanced dialogue management
* Autonomous movement

These features may be considered for future versions.

---

# 🔮 Future Development

Possible future improvements:

### CLARO V2

* Improved speech recognition
* Better natural-language understanding
* More accurate campus search
* Display interface
* Servo-based interaction
* LED status indicators

### CLARO V3

* Local or cloud LLM integration
* RAG-based campus knowledge
* Face detection
* User recognition
* Personalized interaction
* Improved conversation memory

### Future Physical Development

* Custom 3D-printed enclosure
* Pan/tilt head
* Display integration
* Camera module
* Better speaker system
* Battery-powered operation
* More compact electronics

---

# 📜 Development Philosophy

CLARO V1 follows a simple principle:

> **Build the basic system first, verify every component, then add intelligence.**

Instead of starting with a complex AI architecture, V1 separates the system into independently testable components:

```text
Hardware
   ↓
Audio
   ↓
Network
   ↓
Speech Recognition
   ↓
Knowledge Search
   ↓
Text-to-Speech
   ↓
Audio Output
```

This makes debugging and future development easier.

---

# 👨‍💻 Project

**Project:** CLARO – Your Intelligent Campus Companion

**Version:** V1

**Developer / Team Lead:** Mamun

**Institution:** Tongmyong University, Busan, South Korea

**Technology Area:**

* Artificial Intelligence
* Embedded Systems
* Speech Processing
* Web Backend
* IoT
* Robotics

---

# 📄 License

This project is currently intended for educational, research, and prototype development.

If you plan to publish the project as open source, add an appropriate license such as MIT after deciding how you want others to use and modify the code.

---

# ⭐ Contributing

Contributions and suggestions are welcome.

For major changes, please discuss the proposed modification before submitting a pull request.

Recommended contribution areas:

* Speech recognition
* Campus information extraction
* ESP32 optimization
* Audio processing
* Hardware integration
* User interface
* Documentation

---

# 🙌 Acknowledgements

CLARO V1 uses open-source technologies including:

* Python
* FastAPI
* Faster-Whisper
* pyttsx3
* FFmpeg
* BeautifulSoup
* Arduino
* ESP32

Built as a student-led campus technology project at Tongmyong University.
