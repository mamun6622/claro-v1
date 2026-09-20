#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include "ESP_I2S.h"

// ============================================================
// CLARO V1
// ESP32-S3 + INMP441 + MAX98357A
// ============================================================

// ---------------- WIFI ----------------

const char* WIFI_SSID = "U+Net2DD0";
const char* WIFI_PASSWORD = "8CD#B9BHB8";

// ---------------- BACKEND ----------------

const char* BACKEND_URL =
    "http://192.168.219.101:8001";

// ---------------- I2S PINS ----------------

// INMP441
#define MIC_BCLK 4
#define MIC_WS   5
#define MIC_DATA 6

// MAX98357A
#define SPK_BCLK 4
#define SPK_WS   5
#define SPK_DATA 18

// ---------------- AUDIO ----------------

#define SAMPLE_RATE 16000
#define RECORD_SECONDS 5

I2SClass I2S;


// ============================================================
// INITIALIZE MICROPHONE
// ============================================================

bool startMicrophone()
{
    Serial.println();
    Serial.println("Starting microphone I2S...");

    // Make sure previous I2S session is stopped
    I2S.end();

    delay(100);

    // Input only
    I2S.setPins(
        MIC_BCLK,
        MIC_WS,
        -1,
        MIC_DATA
    );

    bool ok = I2S.begin(
        I2S_MODE_STD,
        SAMPLE_RATE,
        I2S_DATA_BIT_WIDTH_32BIT,
        I2S_SLOT_MODE_MONO,
        I2S_STD_SLOT_LEFT
    );

    if (!ok)
    {
        Serial.println("ERROR: I2S microphone begin failed.");
        return false;
    }

    Serial.println("Microphone I2S initialized.");

    // Give DMA some time to start filling
    delay(100);

    return true;
}


// ============================================================
// WAV HEADER
// ============================================================

void writeWavHeader(
    uint8_t* header,
    uint32_t dataSize
)
{
    uint32_t fileSize = dataSize + 36;

    uint16_t audioFormat = 1;
    uint16_t channels = 1;
    uint32_t sampleRate = SAMPLE_RATE;
    uint16_t bitsPerSample = 16;

    uint32_t byteRate =
        sampleRate *
        channels *
        bitsPerSample / 8;

    uint16_t blockAlign =
        channels *
        bitsPerSample / 8;

    memcpy(header, "RIFF", 4);

    header[4] = fileSize & 0xFF;
    header[5] = (fileSize >> 8) & 0xFF;
    header[6] = (fileSize >> 16) & 0xFF;
    header[7] = (fileSize >> 24) & 0xFF;

    memcpy(header + 8, "WAVE", 4);

    memcpy(header + 12, "fmt ", 4);

    header[16] = 16;
    header[17] = 0;
    header[18] = 0;
    header[19] = 0;

    header[20] = audioFormat;
    header[21] = 0;

    header[22] = channels;
    header[23] = 0;

    header[24] = sampleRate & 0xFF;
    header[25] = (sampleRate >> 8) & 0xFF;
    header[26] = (sampleRate >> 16) & 0xFF;
    header[27] = (sampleRate >> 24) & 0xFF;

    header[28] = byteRate & 0xFF;
    header[29] = (byteRate >> 8) & 0xFF;
    header[30] = (byteRate >> 16) & 0xFF;
    header[31] = (byteRate >> 24) & 0xFF;

    header[32] = blockAlign;
    header[33] = 0;

    header[34] = bitsPerSample;
    header[35] = 0;

    memcpy(header + 36, "data", 4);

    header[40] = dataSize & 0xFF;
    header[41] = (dataSize >> 8) & 0xFF;
    header[42] = (dataSize >> 16) & 0xFF;
    header[43] = (dataSize >> 24) & 0xFF;
}


// ============================================================
// WAIT FOR MICROPHONE DATA
// ============================================================

bool waitForMicrophone()
{
    Serial.println("Waiting for microphone data...");

    unsigned long start = millis();

    uint8_t testBuffer[256];

    while (millis() - start < 3000)
    {
        size_t bytesRead =
            I2S.readBytes(
                (char*)testBuffer,
                sizeof(testBuffer)
            );

        if (bytesRead > 0)
        {
            Serial.print("Microphone active. Bytes: ");
            Serial.println(bytesRead);

            return true;
        }

        delay(10);
    }

    Serial.println(
        "ERROR: Microphone produced no data."
    );

    return false;
}


// ============================================================
// RECORD
// ============================================================

uint8_t* recordAudio(size_t* outputSize)
{
    *outputSize = 0;

    if (!startMicrophone())
    {
        return nullptr;
    }

    if (!waitForMicrophone())
    {
        I2S.end();
        return nullptr;
    }

    Serial.println();
    Serial.println("================================");
    Serial.println("RECORDING");
    Serial.println("Speak now...");
    Serial.println("================================");

    const uint32_t sampleCount =
        SAMPLE_RATE * RECORD_SECONDS;

    const uint32_t pcmBytes =
        sampleCount * 2;

    const uint32_t wavBytes =
        pcmBytes + 44;

    uint8_t* wav =
        (uint8_t*)malloc(wavBytes);

    if (!wav)
    {
        Serial.println(
            "ERROR: Memory allocation failed."
        );

        I2S.end();

        return nullptr;
    }

    writeWavHeader(
        wav,
        pcmBytes
    );

    uint32_t written = 0;

    int32_t input[128];

    while (written < pcmBytes)
    {
        size_t bytesRead =
            I2S.readBytes(
                (char*)input,
                sizeof(input)
            );

        if (bytesRead == 0)
        {
            Serial.println(
                "WARNING: temporary I2S read timeout."
            );

            delay(5);

            continue;
        }

        int samples =
            bytesRead /
            sizeof(int32_t);

        for (int i = 0; i < samples; i++)
        {
            if (written >= pcmBytes)
                break;

            // Convert INMP441 32-bit sample
            // to signed 16-bit PCM.

            int32_t sample =
                input[i] >> 14;

            if (sample > 32767)
                sample = 32767;

            if (sample < -32768)
                sample = -32768;

            int16_t sample16 =
                (int16_t)sample;

            wav[44 + written] =
                sample16 & 0xFF;

            wav[45 + written] =
                (sample16 >> 8) & 0xFF;

            written += 2;
        }
    }

    I2S.end();

    *outputSize = wavBytes;

    Serial.print("Recorded WAV bytes: ");
    Serial.println(wavBytes);

    return wav;
}


// ============================================================
// UPLOAD AUDIO
// ============================================================

bool uploadAudio(
    uint8_t* wav,
    size_t wavSize
)
{
    String url =
        String(BACKEND_URL) +
        "/upload-audio";

    Serial.println();
    Serial.println("Uploading audio...");
    Serial.println(url);

    HTTPClient http;

    http.begin(url);

    http.addHeader(
        "Content-Type",
        "audio/wav"
    );

    int code =
        http.POST(
            wav,
            wavSize
        );

    Serial.print("HTTP status: ");
    Serial.println(code);

    if (code > 0)
    {
        String response =
            http.getString();

        Serial.println("Backend response:");
        Serial.println(response);
    }

    http.end();

    if (code == 200)
{
    String response =
        http.getString();

    Serial.println(
        "Backend response:"
    );

    Serial.println(
        response
    );

    http.end();

    // No question / no answer
    if (
        response.indexOf(
            "\"question\":\"\""
        ) >= 0
    )
    {
        Serial.println();
        Serial.println(
            "No speech detected."
        );

        Serial.println(
            "Listening again..."
        );

        return false;
    }

    Serial.println();
    Serial.println(
        "Question received."
    );

    return true;
}

    Serial.println(
        "Audio upload failed."
    );

    return false;
}


// ============================================================
// START SPEAKER
// ============================================================

bool startSpeaker()
{
    Serial.println();
    Serial.println(
        "Starting MAX98357A..."
    );

    I2S.end();

    delay(100);

    I2S.setPins(
        SPK_BCLK,
        SPK_WS,
        SPK_DATA,
        -1
    );

    bool ok = I2S.begin(
        I2S_MODE_STD,
        16000,
        I2S_DATA_BIT_WIDTH_16BIT,
        I2S_SLOT_MODE_MONO,
        I2S_STD_SLOT_LEFT
    );

    if (!ok)
    {
        Serial.println(
            "ERROR: Speaker I2S failed."
        );

        return false;
    }

    Serial.println(
        "Speaker I2S ready."
    );

    return true;
}


// ============================================================
// DOWNLOAD + PLAY WAV
// ============================================================

bool playResponse()
{
    String url =
        String(BACKEND_URL) +
        "/audio";

    Serial.println();
    Serial.println(
        "Downloading CLARO response..."
    );

    HTTPClient http;

    http.begin(url);

    int code =
        http.GET();

    Serial.print("HTTP status: ");
    Serial.println(code);

    if (code != 200)
    {
        Serial.println(
            "ERROR: Audio download failed."
        );

        http.end();

        return false;
    }

    int totalSize =
        http.getSize();

    Serial.print(
        "Audio size: "
    );

    Serial.println(totalSize);

    WiFiClient* stream =
        http.getStreamPtr();

    if (!startSpeaker())
    {
        http.end();

        return false;
    }

    // --------------------------------------------------------
    // Skip WAV header
    // --------------------------------------------------------

    uint8_t header[44];

    size_t headerRead = 0;

    unsigned long timeout =
        millis();

    while (
        headerRead < 44 &&
        millis() - timeout < 5000
    )
    {
        if (stream->available())
        {
            size_t available =
                stream->available();

            size_t needed =
                44 - headerRead;

            if (available > needed)
                available = needed;

            size_t n =
                stream->readBytes(
                    (char*)(
                        header +
                        headerRead
                    ),
                    available
                );

            headerRead += n;
        }

        delay(1);
    }

    if (headerRead != 44)
    {
        Serial.println(
            "ERROR: WAV header failed."
        );

        I2S.end();
        http.end();

        return false;
    }

    // --------------------------------------------------------
    // Play PCM
    // --------------------------------------------------------

    Serial.println(
        "Playing CLARO..."
    );

    uint8_t buffer[1024];

    unsigned long lastData =
        millis();

    while (
        http.connected() ||
        stream->available()
    )
    {
        int available =
            stream->available();

        if (available > 0)
        {
            int amount =
                available;

            if (amount >
                (int)sizeof(buffer))
            {
                amount =
                    sizeof(buffer);
            }

            int n =
                stream->readBytes(
                    (char*)buffer,
                    amount
                );

            if (n > 0)
            {
                I2S.write(
                    buffer,
                    n
                );

                lastData =
                    millis();
            }
        }
        else
        {
            delay(2);
        }

        // Prevent endless waiting
        if (
            millis() - lastData >
            5000
        )
        {
            break;
        }
    }

    I2S.end();

    http.end();

    Serial.println(
        "Playback finished."
    );

    return true;
}


// ============================================================
// WIFI
// ============================================================

void connectWiFi()
{
    Serial.println();
    Serial.println(
        "Connecting to WiFi..."
    );

    WiFi.begin(
        WIFI_SSID,
        WIFI_PASSWORD
    );

    int attempts = 0;

    while (
        WiFi.status() != WL_CONNECTED &&
        attempts < 30
    )
    {
        delay(500);

        Serial.print(".");

        attempts++;
    }

    Serial.println();

    if (
        WiFi.status() ==
        WL_CONNECTED
    )
    {
        Serial.println(
            "WiFi connected."
        );

        Serial.print(
            "ESP32 IP: "
        );

        Serial.println(
            WiFi.localIP()
        );
    }
    else
    {
        Serial.println(
            "ERROR: WiFi connection failed."
        );
    }
}


// ============================================================
// SETUP
// ============================================================

void setup()
{
    Serial.begin(115200);

    delay(1500);

    Serial.println();
    Serial.println(
        "================================"
    );
    Serial.println(
        "       CLARO V1 ESP32-S3"
    );
    Serial.println(
        "================================"
    );

    connectWiFi();

    Serial.println();
    Serial.println(
        "CLARO ready."
    );
}


// ============================================================
// LOOP
// ============================================================

void loop()
{
    if (
        WiFi.status() !=
        WL_CONNECTED
    )
    {
        connectWiFi();
    }

    size_t wavSize = 0;

    uint8_t* wav =
        recordAudio(&wavSize);

    if (wav == nullptr)
    {
        Serial.println();
        Serial.println(
            "Recording failed."
        );

        delay(2000);

        return;
    }

    bool uploaded =
    uploadAudio(
        wav,
        wavSize
    );

free(wav);

if (uploaded)
{
    delay(100);

    playResponse();
}
else
{
    // No speech.
    // Do not play anything.

    Serial.println(
        "Nothing to answer."
    );
}

    Serial.println();
    Serial.println(
        "================================"
    );

    Serial.println(
        "Cycle complete."
    );

    Serial.println(
        "================================"
    );

    delay(2000);
}