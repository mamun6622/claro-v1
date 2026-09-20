#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include "ESP_I2S.h"

// ============================================================
// CLARO V1 - ESP32-S3
// Voice Activity Detection Recording
// ============================================================

// -----------------------------
// Wi-Fi
// -----------------------------

const char* WIFI_SSID = "U+Net2DD0";
const char* WIFI_PASSWORD = "8CD#B9BHB8";

// PC backend
const char* BACKEND_URL = "http://192.168.219.101:8001";

// ============================================================
// I2S MICROPHONE - INMP441
// ============================================================

#define MIC_BCLK 4
#define MIC_WS   5
#define MIC_SD   6

// ============================================================
// I2S SPEAKER - MAX98357A
// ============================================================

#define SPK_BCLK 4
#define SPK_LRC  5
#define SPK_DOUT 18

// ============================================================
// AUDIO SETTINGS
// ============================================================

#define SAMPLE_RATE 16000
#define RECORD_SAMPLE_RATE 16000

// Maximum recording time
#define MAX_RECORD_SECONDS 15
#define MAX_SAMPLES (SAMPLE_RATE * MAX_RECORD_SECONDS)

// Silence required before stopping
#define SILENCE_DURATION_MS 500

// Time required for audio level to be above threshold
// before considering it speech
#define SPEECH_CONFIRM_MS 120

// Number of samples used for level detection
#define LEVEL_CHUNK_SAMPLES 256

// ============================================================
// VOICE DETECTION SETTINGS
// ============================================================

// Adjust this if needed after testing.
//
// Higher = less sensitive
// Lower  = more sensitive
//
// Start with 900.
#define SPEECH_THRESHOLD 700

// ============================================================
// I2S OBJECT
// ============================================================

I2SClass I2S;

// ============================================================
// WAV HEADER
// ============================================================

void writeWavHeader(
    uint8_t* buffer,
    uint32_t dataSize,
    uint32_t sampleRate
) {

    uint32_t fileSize = dataSize + 36;

    // RIFF
    buffer[0] = 'R';
    buffer[1] = 'I';
    buffer[2] = 'F';
    buffer[3] = 'F';

    buffer[4] = fileSize & 0xFF;
    buffer[5] = (fileSize >> 8) & 0xFF;
    buffer[6] = (fileSize >> 16) & 0xFF;
    buffer[7] = (fileSize >> 24) & 0xFF;

    // WAVE
    buffer[8] = 'W';
    buffer[9] = 'A';
    buffer[10] = 'V';
    buffer[11] = 'E';

    // fmt
    buffer[12] = 'f';
    buffer[13] = 'm';
    buffer[14] = 't';
    buffer[15] = ' ';

    // PCM chunk size
    buffer[16] = 16;
    buffer[17] = 0;
    buffer[18] = 0;
    buffer[19] = 0;

    // PCM format = 1
    buffer[20] = 1;
    buffer[21] = 0;

    // Mono
    buffer[22] = 1;
    buffer[23] = 0;

    // Sample rate
    buffer[24] = sampleRate & 0xFF;
    buffer[25] = (sampleRate >> 8) & 0xFF;
    buffer[26] = (sampleRate >> 16) & 0xFF;
    buffer[27] = (sampleRate >> 24) & 0xFF;

    // Byte rate
    uint32_t byteRate = sampleRate * 2;

    buffer[28] = byteRate & 0xFF;
    buffer[29] = (byteRate >> 8) & 0xFF;
    buffer[30] = (byteRate >> 16) & 0xFF;
    buffer[31] = (byteRate >> 24) & 0xFF;

    // Block align
    buffer[32] = 2;
    buffer[33] = 0;

    // Bits per sample
    buffer[34] = 16;
    buffer[35] = 0;

    // data
    buffer[36] = 'd';
    buffer[37] = 'a';
    buffer[38] = 't';
    buffer[39] = 'a';

    buffer[40] = dataSize & 0xFF;
    buffer[41] = (dataSize >> 8) & 0xFF;
    buffer[42] = (dataSize >> 16) & 0xFF;
    buffer[43] = (dataSize >> 24) & 0xFF;
}

// ============================================================
// START MICROPHONE
// ============================================================

void startMicrophone() {

    I2S.setPins(
        MIC_BCLK,
        MIC_WS,
        -1,
        MIC_SD,
        -1
    );

    I2S.begin(
        I2S_MODE_STD,
        SAMPLE_RATE,
        I2S_DATA_BIT_WIDTH_32BIT,
        I2S_SLOT_MODE_MONO
    );

    Serial.println("Microphone started.");
}

// ============================================================
// STOP MICROPHONE
// ============================================================

void stopMicrophone() {

    I2S.end();

    Serial.println("Microphone stopped.");
}

// ============================================================
// CALCULATE AUDIO LEVEL
// ============================================================

float calculateAudioLevel(int32_t* samples, int count) {

    if (count <= 0) {
        return 0;
    }

    double sum = 0;

    for (int i = 0; i < count; i++) {

        int32_t sample = samples[i];

        // Convert 32-bit I2S value to approximate 16-bit
        sample = sample >> 14;

        if (sample < 0) {
            sample = -sample;
        }

        sum += sample;
    }

    return sum / count;
}

// ============================================================
// READ AUDIO CHUNK
// ============================================================

int readMicChunk(
    int32_t* buffer,
    int samplesToRead
) {

    size_t bytesRead = 0;

    I2S.readBytes(
        (char*)buffer,
        samplesToRead * sizeof(int32_t)
    );

    bytesRead = samplesToRead * sizeof(int32_t);

    return bytesRead / sizeof(int32_t);
}

// ============================================================
// RECORD UNTIL SILENCE
// ============================================================

uint8_t* recordUntilSilence(
    size_t& wavSize
) {

    Serial.println();
    Serial.println("==============================");
    Serial.println("CLARO VOICE DETECTION");
    Serial.println("==============================");

    Serial.println("Waiting for speech...");

    // --------------------------------------------------------
    // Allocate maximum possible WAV buffer
    // --------------------------------------------------------

    size_t maxDataSize =
        MAX_SAMPLES * sizeof(int16_t);

    size_t maxWavSize =
        44 + maxDataSize;

    uint8_t* wav =
        (uint8_t*)malloc(maxWavSize);

    if (!wav) {

        Serial.println(
            "ERROR: Could not allocate recording buffer."
        );

        wavSize = 0;

        return nullptr;
    }

    // --------------------------------------------------------
    // Temporary microphone buffer
    // --------------------------------------------------------

    int32_t* micBuffer =
        (int32_t*)malloc(
            LEVEL_CHUNK_SAMPLES *
            sizeof(int32_t)
        );

    if (!micBuffer) {

        Serial.println(
            "ERROR: Could not allocate microphone buffer."
        );

        free(wav);

        wavSize = 0;

        return nullptr;
    }

    // --------------------------------------------------------
    // Start microphone
    // --------------------------------------------------------

    startMicrophone();

    delay(100);

    // --------------------------------------------------------
    // Flush initial microphone data
    // --------------------------------------------------------

    for (int i = 0; i < 3; i++) {

        readMicChunk(
            micBuffer,
            LEVEL_CHUNK_SAMPLES
        );
    }

    // --------------------------------------------------------
    // WAIT FOR SPEECH
    // --------------------------------------------------------

    bool speechStarted = false;

    unsigned long speechStartCandidate = 0;

    while (!speechStarted) {

        int count = readMicChunk(
            micBuffer,
            LEVEL_CHUNK_SAMPLES
        );

        float level =
            calculateAudioLevel(
                micBuffer,
                count
            );

        Serial.print(
            "Waiting level: "
        );

        Serial.println(level);

        if (level >= SPEECH_THRESHOLD) {

            if (speechStartCandidate == 0) {

                speechStartCandidate =
                    millis();
            }

            if (
                millis() -
                speechStartCandidate >=
                SPEECH_CONFIRM_MS
            ) {

                speechStarted = true;

                Serial.println();
                Serial.println(
                    ">>> SPEECH DETECTED <<<"
                );

            }

        } else {

            speechStartCandidate = 0;
        }
    }

    // --------------------------------------------------------
    // RECORDING
    // --------------------------------------------------------

    Serial.println("Recording...");

    uint32_t sampleCount = 0;

    unsigned long recordingStart =
        millis();

    unsigned long lastSpeechTime =
        millis();

    // --------------------------------------------------------
    // Small pre-buffer
    //
    // We keep the first detected chunk so the
    // beginning of the user's sentence isn't lost.
    // --------------------------------------------------------

    for (int i = 0; i < LEVEL_CHUNK_SAMPLES; i++) {

        if (sampleCount >= MAX_SAMPLES) {
            break;
        }

        int32_t sample =
            micBuffer[i];

        int16_t pcm =
            (int16_t)(sample >> 14);

        uint8_t* destination =
            wav +
            44 +
            (sampleCount * 2);

        destination[0] =
            pcm & 0xFF;

        destination[1] =
            (pcm >> 8) & 0xFF;

        sampleCount++;
    }

    // --------------------------------------------------------
    // CONTINUE RECORDING
    // --------------------------------------------------------

    while (sampleCount < MAX_SAMPLES) {

        int count = readMicChunk(
            micBuffer,
            LEVEL_CHUNK_SAMPLES
        );

        if (count <= 0) {
            continue;
        }

        float level =
            calculateAudioLevel(
                micBuffer,
                count
            );

        // --------------------------------------------
        // Convert microphone data to 16-bit PCM
        // --------------------------------------------

        for (int i = 0; i < count; i++) {

            if (sampleCount >= MAX_SAMPLES) {
                break;
            }

            int32_t sample =
                micBuffer[i];

            int16_t pcm =
                (int16_t)(sample >> 14);

            uint8_t* destination =
                wav +
                44 +
                (sampleCount * 2);

            destination[0] =
                pcm & 0xFF;

            destination[1] =
                (pcm >> 8) & 0xFF;

            sampleCount++;
        }

        // --------------------------------------------
        // Speech detected
        // --------------------------------------------

        if (level >= SPEECH_THRESHOLD) {

            lastSpeechTime =
                millis();

            Serial.print(
                "Speaking | Level: "
            );

            Serial.println(level);
        }

        // --------------------------------------------
        // Silence detected
        // --------------------------------------------

        else {

            unsigned long silenceTime =
                millis() -
                lastSpeechTime;

            Serial.print(
                "Silence | Level: "
            );

            Serial.print(level);

            Serial.print(
                " | Silence: "
            );

            Serial.print(silenceTime);

            Serial.println(" ms");

            if (
                silenceTime >=
                SILENCE_DURATION_MS
            ) {

                Serial.println();
                Serial.println(
                    ">>> END OF SPEECH <<<"
                );

                break;
            }
        }

        // --------------------------------------------
        // Maximum recording time
        // --------------------------------------------

        if (
            millis() -
            recordingStart >=
            MAX_RECORD_SECONDS * 1000UL
        ) {

            Serial.println();
            Serial.println(
                ">>> MAX RECORDING TIME <<<"
            );

            break;
        }
    }

    // --------------------------------------------------------
    // Stop microphone
    // --------------------------------------------------------

    stopMicrophone();

    // --------------------------------------------------------
    // Create WAV header
    // --------------------------------------------------------

    uint32_t dataSize =
        sampleCount * sizeof(int16_t);

    wavSize =
        44 + dataSize;

    writeWavHeader(
        wav,
        dataSize,
        SAMPLE_RATE
    );

    // --------------------------------------------------------
    // Cleanup temporary buffer
    // --------------------------------------------------------

    free(micBuffer);

    // --------------------------------------------------------
    // Print result
    // --------------------------------------------------------

    float duration =
        (float)sampleCount /
        SAMPLE_RATE;

    Serial.println();
    Serial.println(
        "Recording complete."
    );

    Serial.print(
        "Samples: "
    );

    Serial.println(sampleCount);

    Serial.print(
        "Duration: "
    );

    Serial.print(duration, 2);

    Serial.println(" seconds");

    Serial.print(
        "WAV size: "
    );

    Serial.print(wavSize);

    Serial.println(" bytes");

    Serial.println(
        "=============================="
    );

    return wav;
}

// ============================================================
// UPLOAD AUDIO TO BACKEND
// ============================================================

bool uploadAudio(
    uint8_t* wav,
    size_t wavSize
) {

    if (!wav || wavSize == 0) {

        Serial.println(
            "No audio to upload."
        );

        return false;
    }

    Serial.println();
    Serial.println(
        "Uploading audio..."
    );

    HTTPClient http;

    String url =
        String(BACKEND_URL) +
        "/upload-audio";

    http.begin(url);

    http.addHeader(
        "Content-Type",
        "audio/wav"
    );

    http.setTimeout(30000);

    int httpCode =
        http.POST(
            wav,
            wavSize
        );

    Serial.print(
        "HTTP status: "
    );

    Serial.println(httpCode);

    if (httpCode != 200) {

        Serial.println(
            "Audio upload failed."
        );

        http.end();

        return false;
    }

    // IMPORTANT:
    // Read response BEFORE http.end()
    String response =
        http.getString();

    Serial.println(
        "Backend response:"
    );

    Serial.println(response);

    http.end();

    // --------------------------------------------------------
    // No speech detected
    // --------------------------------------------------------

    if (
        response.indexOf(
            "\"question\":\"\""
        ) >= 0
    ) {

        Serial.println(
            "Backend detected no speech."
        );

        return false;
    }

    // --------------------------------------------------------
    // Real question detected
    // --------------------------------------------------------

    Serial.println(
        "Question detected."
    );

    return true;
}

// ============================================================
// SPEAKER START
// ============================================================

void startSpeaker() {

    I2S.setPins(
        SPK_BCLK,
        SPK_LRC,
        SPK_DOUT,
        -1,
        -1
    );

    I2S.begin(
        I2S_MODE_STD,
        SAMPLE_RATE,
        I2S_DATA_BIT_WIDTH_16BIT,
        I2S_SLOT_MODE_MONO
    );

    Serial.println(
        "Speaker started."
    );
}

// ============================================================
// PLAY RESPONSE
// ============================================================

void playResponse() {

    Serial.println();
    Serial.println(
        "Downloading response audio..."
    );

    HTTPClient http;

    String url =
        String(BACKEND_URL) +
        "/audio";

    http.begin(url);

    http.setTimeout(30000);

    int httpCode =
        http.GET();

    Serial.print(
        "Audio HTTP status: "
    );

    Serial.println(httpCode);

    if (httpCode != 200) {

        Serial.println(
            "Failed to download response."
        );

        http.end();

        return;
    }

    WiFiClient* stream =
        http.getStreamPtr();

    // --------------------------------------------------------
    // Skip WAV header
    // --------------------------------------------------------

    uint8_t header[44];

    int headerRead = 0;

    unsigned long headerStart =
        millis();

    while (
        headerRead < 44 &&
        millis() - headerStart < 5000
    ) {

        if (stream->available()) {

            int available =
                stream->available();

            int needed =
                44 - headerRead;

            int toRead =
                min(
                    available,
                    needed
                );

            int received =
                stream->readBytes(
                    header + headerRead,
                    toRead
                );

            headerRead += received;

        } else {

            delay(1);
        }
    }

    if (headerRead < 44) {

        Serial.println(
            "Could not read WAV header."
        );

        http.end();

        return;
    }

    Serial.println(
        "WAV header received."
    );

    // --------------------------------------------------------
    // Start speaker
    // --------------------------------------------------------

    startSpeaker();

    // --------------------------------------------------------
    // Stream audio
    // --------------------------------------------------------

    uint8_t audioBuffer[2048];

    unsigned long lastData =
        millis();

    while (
        http.connected() ||
        stream->available()
    ) {

        int available =
            stream->available();

        if (available > 0) {

            int toRead =
                min(
                    available,
                    (int)sizeof(audioBuffer)
                );

            int received =
                stream->readBytes(
                    audioBuffer,
                    toRead
                );

            if (received > 0) {

                I2S.write(
                    audioBuffer,
                    received
                );

                lastData =
                    millis();
            }

        } else {

            if (
                millis() -
                lastData > 3000
            ) {

                break;
            }

            delay(1);
        }
    }

    // --------------------------------------------------------
    // Stop speaker
    // --------------------------------------------------------

    I2S.end();

    http.end();

    Serial.println(
        "Response playback complete."
    );
}

// ============================================================
// CONNECT WIFI
// ============================================================

void connectWiFi() {

    Serial.println();
    Serial.println(
        "Connecting to Wi-Fi..."
    );

    WiFi.mode(WIFI_STA);

    WiFi.begin(
        WIFI_SSID,
        WIFI_PASSWORD
    );

    int attempts = 0;

    while (
        WiFi.status() != WL_CONNECTED &&
        attempts < 40
    ) {

        delay(500);

        Serial.print(".");

        attempts++;
    }

    Serial.println();

    if (
        WiFi.status() ==
        WL_CONNECTED
    ) {

        Serial.println(
            "Wi-Fi connected."
        );

        Serial.print(
            "ESP32 IP: "
        );

        Serial.println(
            WiFi.localIP()
        );

    } else {

        Serial.println(
            "Wi-Fi connection failed."
        );
    }
}

// ============================================================
// SETUP
// ============================================================

void setup() {

    Serial.begin(115200);

    delay(1500);

    Serial.println();
    Serial.println(
        "================================"
    );
    Serial.println(
        "       CLARO V1"
    );
    Serial.println(
        " Voice Activity Detection"
    );
    Serial.println(
        "================================"
    );

    connectWiFi();

    Serial.println();
    Serial.println(
        "CLARO is ready."
    );
}

// ============================================================
// LOOP
// ============================================================

void loop() {

    // --------------------------------------------------------
    // Make sure Wi-Fi is connected
    // --------------------------------------------------------

    if (
        WiFi.status() !=
        WL_CONNECTED
    ) {

        Serial.println(
            "Wi-Fi disconnected."
        );

        connectWiFi();

        delay(1000);

        return;
    }

    // --------------------------------------------------------
    // Wait for speech and record
    // --------------------------------------------------------

    size_t wavSize = 0;

    uint8_t* wav =
        recordUntilSilence(
            wavSize
        );

    // --------------------------------------------------------
    // Recording failed
    // --------------------------------------------------------

    if (!wav || wavSize == 0) {

        Serial.println(
            "Recording failed."
        );

        if (wav) {
            free(wav);
        }

        delay(500);

        return;
    }

    // --------------------------------------------------------
    // Upload
    // --------------------------------------------------------

    bool uploaded =
        uploadAudio(
            wav,
            wavSize
        );

    // --------------------------------------------------------
    // Free recording memory
    // --------------------------------------------------------

    free(wav);

    wav = nullptr;

    // --------------------------------------------------------
    // Play response only if a real question exists
    // --------------------------------------------------------

    if (uploaded) {

        delay(100);

        playResponse();

    } else {

        Serial.println(
            "Nothing to answer."
        );
    }

    Serial.println();
    Serial.println(
        "Returning to voice detection..."
    );

    delay(200);
}