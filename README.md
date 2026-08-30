# VCaaS — Voice Clone as a Service

VCaaS is a creator-first, ethical voice cloning platform built with Next.js (Frontend) and FastAPI (Backend). It empowers creators with high-quality voice synthesis while protecting against misuse through state-of-the-art cryptographic watermarking and deepfake detection APIs.

## 🌟 Core Features

### 1. Zero-Shot Voice Cloning (TTS)
- Clone voices using just a short reference audio file (via **XTTS v2**).
- Fine-grained control over text-to-speech generation.
- **Auto-Watermarking**: A cryptographic, inaudible high-frequency sine-wave watermark (19kHz) is automatically embedded into every generated audio file to prove its origin.

### 2. 6-Layer Deepfake Defense System
A military-grade audio analysis tool available at `/security`. Upload any audio file to run it through 6 layers of verification:
1. **Acoustic Anti-Spoofing:** Analyzes phase variance, zero-crossing rates, and high-frequency ratios.
2. **Speaker Consistency:** (Requires reference) Verifies biometric identity.
3. **Prosody Analysis:** Checks pitch stability and voiced frame consistency.
4. **Paralinguistic Analysis:** Detects abnormal emotional arousal and spectral contrast.
5. **Semantic Coherence:** Whisper-powered transcription to check speech rate and pause consistency.
6. **Cryptographic Watermark Detection:** Scans for the proprietary MVP Sine-wave signature. If found, automatically flags the audio as a **Deepfake (Watermarked Synthetic)** with 100% confidence.

### 3. Premium Admin & Dashboard UI
- **Minimalist Dark Mode:** A sleek, high-contrast UI across the platform.
- **Admin Dashboard:** Server-side protected `/admin/dashboard` providing real-time system metrics, user stats, and license monitoring.
- **User Authentication:** Email-only login powered by Firebase.

## 🛠 Tech Stack

- **Frontend:** Next.js (React), TailwindCSS, Axios
- **Backend:** Python (FastAPI), Uvicorn, Coqui TTS (XTTS v2)
- **Database:** SQLite / Firebase
- **Hosting:** Vercel (Frontend) & Render (Backend)

## 🚀 How to Use the Platform

### Running Locally (Development)
The easiest way to run the stack locally is via Docker, as the backend relies on specific Python versions (3.11 recommended) and audio processing libraries (`pydub`, `audioop`).

1. **Start the Backend and DB via Docker:**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```
2. **Start the Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Using the Live Deployed Application
The platform is fully deployed and accessible via the web.
- **Frontend URL:** `https://vcaas-rbu8.vercel.app`
- **Backend API URL:** `https://vcaas.onrender.com`
- **Developer API Documentation:** `https://vcaas-rbu8.vercel.app/docs`

#### **Generating Watermarked Audio**
1. Navigate to the **Playground** (`/playground`).
2. Type in your desired text.
3. Upload a reference voice sample.
4. Check the **"Apply invisible watermark"** box.
5. Hit Generate. The downloaded `.wav` file contains the cryptographic signature.

#### **Verifying Deepfakes**
1. Navigate to the **Security** page (`/security`).
2. Upload any audio clip (such as the one you just generated).
3. The system will process it through the 6-layer defense and provide a definitive authenticity verdict.

#### **API Access (Terminal Testing)**
You can hit the live backend API directly from your terminal.

**1. Create a dummy reference file:**
```bash
python -c "import wave, struct; f=wave.open('test.wav','w'); f.setnchannels(1); f.setsampwidth(2); f.setframerate(44100); f.writeframes(b'\x00' * 44100 * 2); f.close()"
```

**2. Generate Cloned Audio (Outputs `result.wav`):**
```bash
curl -X POST -F "text=Testing the invisible acoustic watermark." -F "language=en" -F "reference=@test.wav" https://vcaas.onrender.com/api/v1/tts/clone --output result.wav
```

**3. Verify the Output via the 6-Layer Defense:**
```bash
curl -X POST -F "file=@result.wav" https://vcaas.onrender.com/api/v1/verify/full-analysis
```
