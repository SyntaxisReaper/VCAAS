# VCaaS — Voice Clone as a Service

*Creator-first, ethical voice cloning with watermarking, licensing, and API access*

VCaaS is a full-stack SaaS platform that lets creators upload voice samples, train personalized voice models, synthesize speech, license their voices, and enforce traceability via inaudible watermarks. The platform combines a Next.js web app with a FastAPI backend powered by Coqui XTTS v2, multi-layer watermarking, and token-based licensing.

---

## 🎯 Core Features

- 🎤 **Voice Upload & Training** — Guided upload wizard with VAD, SNR checks, spectral analysis, and anti-spoofing detection
- 🧠 **Zero-Shot Voice Cloning** — High-quality TTS from a short reference sample using XTTS v2 (no training required)
- 🏋️ **Fine-Tuned Voice Models** — Full training pipeline for personalized, high-fidelity voice models
- 🌊 **Multi-Layer Watermarking** — Inaudible spread-spectrum embedding with Reed-Solomon FEC for tamper resistance
- 📜 **Licensing System** — Token-based licenses (Personal / Commercial / Enterprise / Educational) with usage tracking
- 🎮 **Voice Playground** — Type-to-speak with real-time synthesis, audio visualization, and download
- 📊 **Usage Analytics** — Comprehensive logs for API calls, synthesis jobs, and voice usage
- 🔍 **Watermark Verification** — Detect & decode embedded watermarks from uploaded audio (single or batch)
- 🔌 **Developer API** — REST API with Firebase auth + JWT for programmatic access
- 👤 **Admin Console** — User management and platform monitoring

---

## 🏗️ Architecture

```
┌────────────────────────────┐     ┌─────────────────────────────┐
│   Frontend (Next.js 16)    │     │   Backend (FastAPI)          │
│   localhost:3001           │────►│   localhost:8000             │
│                            │     │                             │
│  • Landing / Marketing     │     │  API v1:                    │
│  • Dashboard               │     │  • /auth  (Firebase + JWT)  │
│  • Playground (TTS)        │     │  • /voices                  │
│  • Voice Training          │     │  • /tts   (clone + synth)   │
│  • Licensing               │     │  • /licenses                │
│  • Billing / Profile       │     │  • /verify (watermark)      │
│  • Admin Panel             │     │  • /training                │
│  • Security Reports        │     │                             │
└────────────────────────────┘     └─────────────────────────────┘
                                              │
              ┌───────────────────────────────┼──────────────────┐
              ▼                               ▼                  ▼
   ┌──────────────────┐        ┌──────────────────────┐  ┌──────────────┐
   │  Firebase        │        │  Coqui XTTS v2       │  │  AWS S3 /    │
   │  • Auth          │        │  • Zero-shot clone   │  │  GCS         │
   │  • Firestore     │        │  • Fine-tune TTS     │  │  Audio files │
   │  • Realtime DB   │        │  • SpeechBrain       │  │  Model artfs │
   └──────────────────┘        │    (ECAPA speaker    │  └──────────────┘
                               │     verification)    │
                               │  • Faster-Whisper    │
                               │    (STT alignment)   │
                               └──────────────────────┘
                                          │
                          ┌───────────────┴───────────────┐
                          ▼                               ▼
               ┌──────────────────┐          ┌───────────────────┐
               │  SQLite (dev)    │          │  Redis + Celery   │
               │  PostgreSQL      │          │  Background jobs  │
               │  (production)    │          │  Flower monitor   │
               └──────────────────┘          └───────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| Next.js | 16 (App Router) | React framework |
| React | 18.3 | UI library |
| TypeScript | 5 | Type safety |
| Tailwind CSS | 3 | Utility-first styling |
| Framer Motion | 10 | Animations & transitions |
| Firebase JS SDK | 12 | Client-side auth |
| Axios | 1.6 | HTTP client |
| WaveSurfer.js | 7 | Audio waveform visualization |
| Three.js / R3F | 0.160 / 8.15 | 3D canvas effects |
| Lucide React | 0.303 | Icon set |

### Backend
| Technology | Version | Purpose |
|---|---|---|
| FastAPI | 0.104 | Async REST framework |
| Python | 3.10+ | Language |
| SQLAlchemy | 2.0 | ORM (async + sync) |
| Alembic | 1.13 | Database migrations |
| Pydantic v2 | ≥2.5 | Request/response schemas |
| Firebase Admin | 6.3 | Server-side token verification |
| PyJWT | 2.8 | Custom JWT issuance |
| Celery | 5.3 | Background task queue |
| Redis | 5.0 | Cache + Celery broker |

### AI / ML
| Technology | Purpose |
|---|---|
| Coqui TTS (XTTS v2) | Zero-shot voice cloning & fine-tuned TTS |
| PyTorch ≥2.2 | Model inference |
| Transformers ≥4.36 | Hugging Face model utilities |
| SpeechBrain 0.5 | ECAPA-TDNN speaker verification |
| Faster-Whisper ≥0.10 | STT for semantic alignment |
| librosa / soundfile | Audio feature extraction & processing |
| Reed-Solomon (`reedsolo`) | FEC for watermark payload |

---

## 📁 Project Structure

```
VCAAS/
├── frontend/                        # Next.js 16 App Router application
│   └── src/
│       ├── app/                     # Pages (file-system routing)
│       │   ├── page.tsx             # Landing page
│       │   ├── layout.tsx           # Root layout
│       │   ├── globals.css          # Global styles & design tokens
│       │   ├── dashboard/           # User dashboard
│       │   ├── playground/          # TTS playground
│       │   ├── training/            # Voice training flow
│       │   ├── billing/             # Subscription & billing
│       │   ├── licensing/           # License management
│       │   ├── profile/             # User profile
│       │   ├── settings/            # Account settings
│       │   ├── security/            # Security reports
│       │   ├── admin/               # Admin panel
│       │   ├── auth/, login/, signup/  # Auth flows
│       │   ├── effects/             # Audio effects
│       │   ├── help/                # Help center
│       │   └── pricing/             # Pricing page
│       ├── components/
│       │   ├── layout/Navbar.tsx    # Global navigation bar
│       │   ├── dashboard/           # Dashboard widgets
│       │   ├── training/            # Training UI components
│       │   ├── ui/                  # Design system atoms
│       │   ├── common/              # Shared components
│       │   ├── providers/           # React context providers
│       │   ├── SignInCanvasLogin.tsx # Canvas login overlay
│       │   ├── VaporizeTextCycle.tsx # Hero animation
│       │   └── Dock.tsx             # macOS-style dock
│       ├── lib/
│       │   ├── api.ts               # Axios API client
│       │   ├── firebase.ts          # Firebase SDK wrapper (auth)
│       │   ├── voiceCloning.ts      # Zero-shot cloning helpers
│       │   ├── trainingPipeline.ts  # Training orchestration
│       │   ├── advancedTTS.ts       # TTS feature set
│       │   ├── licensing.ts         # License management client
│       │   ├── watermarking.ts      # Client-side watermark utils
│       │   ├── subscription.ts      # Subscription management
│       │   └── adminAuth.ts         # Admin auth helpers
│       ├── contexts/ThemeContext.tsx
│       ├── hooks/                   # Custom React hooks
│       └── types/                   # TypeScript type definitions
│
├── backend/                         # FastAPI application
│   ├── main.py                      # Entry point (imports app.main)
│   └── app/
│       ├── main.py                  # App factory, middleware, router mounts
│       ├── api/v1/
│       │   ├── auth.py              # Register, login, profile
│       │   ├── otp.py               # Email OTP request/verify
│       │   ├── users.py             # User sync (Firebase → DB)
│       │   ├── voices.py            # Voice CRUD
│       │   ├── tts.py               # TTS synthesis & voice clone
│       │   ├── licenses.py          # License issuance & verification
│       │   └── verify.py            # Watermark detection & forensics
│       ├── core/
│       │   ├── config.py            # Pydantic settings (env-driven)
│       │   ├── database.py          # SQLAlchemy async + sync engines
│       │   ├── auth.py              # JWT dependency guards
│       │   ├── firebase_auth.py     # Firebase Admin token verification
│       │   ├── security.py          # Password hashing, JWT creation
│       │   └── watermark.py         # Core watermark algorithm
│       ├── models/                  # SQLAlchemy ORM models
│       │   ├── user.py, voice.py
│       │   ├── license.py, usage_log.py, watermark.py
│       ├── schemas/                 # Pydantic request/response schemas
│       └── services/                # Business logic layer
│           ├── tts_service.py               # Async TTS job manager
│           ├── tts_inference_engine.py      # Coqui XTTS runner
│           ├── voice_cloning_service.py     # Clone orchestration
│           ├── voice_training_service.py    # Training pipeline
│           ├── voice_processor.py           # Audio preprocessing
│           ├── audio_processor.py           # Audio utilities
│           ├── voice_preview_generator.py   # Quick preview synthesis
│           ├── watermark.py                 # Watermark embed/detect
│           ├── forensics_service.py         # Forensic audio analysis
│           ├── semantic_service.py          # Whisper STT alignment
│           ├── speaker_verification.py      # ECAPA-TDNN verify
│           ├── antispoof.py                 # Anti-spoofing detection
│           ├── storage.py                   # S3/GCS file manager
│           ├── auth.py                      # Auth service logic
│           ├── otp_service.py               # OTP generation & delivery
│           ├── license_service.py           # License business logic
│           └── prosody_service.py           # Prosody/style analysis
│
├── Training/                        # Training scripts & data
├── tests/                           # Integration & E2E tests
├── scripts/                         # Utility scripts
├── docs/                            # Additional documentation
├── docker-compose.yml               # Production compose
├── docker-compose.dev.yml           # Full dev stack (Postgres, Redis, Nginx)
└── vercel.json                      # Frontend Vercel deployment config
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js ≥ 20.9** and npm ≥ 8
- **Python 3.10+**
- **Git**
- **Redis** (optional for local dev — background jobs degrade gracefully without it)
- **NVIDIA GPU** (recommended for ML inference; CPU works but is slow)

> **Note:** For a fully containerised setup with PostgreSQL, Redis, Celery, and Nginx, use Docker (see [Docker Setup](#-docker-setup) below).

---

### Local Development (without Docker)

#### 1. Clone the repository

```bash
git clone <your-repo-url>
cd VCAAS
```

#### 2. Backend setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — at minimum set FIREBASE_* and SECRET_KEY

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will auto-create a local SQLite database (`vcaas_dev.db`) on first run — no separate database setup needed for development.

#### 3. Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Edit .env.local — set NEXT_PUBLIC_FIREBASE_* and NEXT_PUBLIC_API_URL

# Start development server
npm run dev
```

#### 4. Access the application

| Service | URL |
|---|---|
| Frontend | http://localhost:3001 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

### 🐳 Docker Setup

Full dev stack with PostgreSQL, Redis, Celery, Flower monitor, and Nginx:

```bash
# From the project root
docker-compose -f docker-compose.dev.yml up --build
```

| Service | Port |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Celery Flower | http://localhost:5555 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |
| Nginx proxy | http://localhost:80 |

---

## 🔗 API Reference

### Authentication
```
POST /api/v1/auth/register          # Register with email + password
POST /api/v1/auth/login             # Login → JWT
GET  /api/v1/auth/profile           # Get current user profile
POST /api/v1/auth/otp/request       # Request email OTP
POST /api/v1/auth/otp/verify        # Verify OTP → Firebase custom token
POST /api/v1/users/sync             # Sync Firebase user to backend DB
```

### Voice Management
```
GET    /api/v1/voices               # List user's voices
POST   /api/v1/voices               # Upload a new voice sample
GET    /api/v1/voices/{id}          # Get voice details
DELETE /api/v1/voices/{id}          # Delete a voice
```

### Text-to-Speech
```
POST /api/v1/tts/generate           # Async TTS job (returns job ID)
GET  /api/v1/tts/jobs               # List TTS jobs
GET  /api/v1/tts/jobs/{id}          # Poll job status
POST /api/v1/tts/clone              # Zero-shot voice clone (multipart audio)
POST /api/v1/tts/clone/warmup       # Warm up XTTS model
```

### Licensing
```
GET  /api/v1/licenses               # List licenses
POST /api/v1/licenses               # Issue a new license
GET  /api/v1/licenses/{id}          # Get license details
PUT  /api/v1/licenses/{id}          # Update license
```

### Watermark Verification
```
POST /api/v1/verify                 # Detect watermark in uploaded audio
POST /api/v1/verify/batch           # Batch watermark detection
GET  /api/v1/verify/{id}            # Get verification result
```

### System
```
GET /health                         # Health check (DB + TTS service)
GET /stats                          # System statistics
GET /api/v1/info                    # API capabilities & limits
```

---

## 🌊 Watermarking Technology

VCaaS uses a multi-layer watermarking system applied to every synthesized audio file:

| Layer | Method | Resistance |
|---|---|---|
| Layer 1 | MVP sine embedding at ~19kHz | Basic identification |
| Layer 2 | Spread-spectrum (multi-band) | Noise & compression |
| Layer 3 | Reed-Solomon FEC payload | Bit errors & corruption |
| Layer 4 | Cryptographic signing | Tampering & forgery |

Verification is available via `POST /api/v1/verify` with the audio file — the API returns the decoded watermark ID, voice owner, and creation timestamp.

---

## 🔒 Authentication Flow

```
User → Firebase Auth (Google / Email / OTP)
     → Firebase ID Token
     → Backend: POST /api/v1/users/sync (Bearer: ID Token)
     → Backend validates token via Firebase Admin SDK
     → User record created/updated in SQLite/PostgreSQL
     → Backend issues its own JWT for subsequent API calls
```

---

## ⚙️ Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | JWT signing secret (≥32 chars) |
| `DATABASE_URL` | ✅ | SQLite (`sqlite+aiosqlite:///./vcaas_dev.db`) or PostgreSQL URL |
| `FIREBASE_PROJECT_ID` | ✅ | Firebase project ID |
| `FIREBASE_PRIVATE_KEY` | ✅ | Firebase Admin SDK private key |
| `FIREBASE_CLIENT_EMAIL` | ✅ | Firebase Admin SDK client email |
| `FIREBASE_PRIVATE_KEY_ID` | ✅ | Firebase private key ID |
| `FIREBASE_CLIENT_ID` | ✅ | Firebase client ID |
| `AWS_ACCESS_KEY_ID` | ✅ | AWS S3 access key |
| `AWS_SECRET_ACCESS_KEY` | ✅ | AWS S3 secret key |
| `AWS_S3_BUCKET` | ✅ | S3 bucket name |
| `WATERMARK_KEY` | ✅ | Watermark signing key (≥32 chars) |
| `REDIS_URL` | ➖ | Redis URL (default: `redis://localhost:6379`) |
| `DEBUG` | ➖ | `true` for development |
| `LOG_LEVEL` | ➖ | `DEBUG` / `INFO` / `WARNING` |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | Backend URL (default: `http://localhost:8000`) |
| `NEXT_PUBLIC_FIREBASE_API_KEY` | Firebase web API key |
| `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` | Firebase auth domain |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID` | Firebase project ID |
| `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET` | Firebase storage bucket |
| `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID` | Firebase messaging sender ID |
| `NEXT_PUBLIC_FIREBASE_APP_ID` | Firebase app ID |

---

## 📊 Roadmap

### MVP ✅
- [x] Landing page + auth flows (Google, Email, OTP)
- [x] Voice upload with quality checks (VAD, SNR, spectral)
- [x] Zero-shot voice cloning (XTTS v2)
- [x] Multi-layer watermark embedding + verification
- [x] Licensing system with token generation
- [x] Dashboard, Playground, Training, Billing pages
- [x] Firebase + SQLAlchemy dual-persistence

### v1 🚧
- [ ] Fix API endpoint alignment between frontend `lib/api.ts` and backend routes
- [ ] Complete Navbar auth integration (user avatar, sign-out)
- [ ] Stripe/payment integration for billing page
- [ ] Usage analytics charts on dashboard
- [ ] Production PostgreSQL deployment

### v2 📋
- [ ] Voice Marketplace — creators sell licenses to brands
- [ ] Multi-lingual support with accent preservation
- [ ] Unity / Unreal Engine SDK plugins
- [ ] Enhanced admin console with takedown workflow

### v3 🔮
- [ ] Music & singing voice styles
- [ ] Identity verification services
- [ ] SSO / SAML for enterprise
- [ ] On-premises deployment option

---

## 🛡️ Security & Compliance

- **Voice consent flow** with explicit agreements before cloning
- **Inaudible watermark** on every generated audio for traceability
- **Firebase token verification** on every authenticated endpoint
- **GDPR-ready** data model with deletion capabilities
- **Rate limiting** (100 req/min default, configurable)
- **TLS 1.3** in transit, **AES-256** at rest (S3 server-side encryption)

---

## 📚 Documentation

- [Production Deployment Guide](PRODUCTION_DEPLOYMENT_GUIDE.md)
- [API Docs (live)](http://localhost:8000/docs)
- [Auth Redesign Notes](vcaas-auth-redesign.md)
- [Repo Audit](vcaas-repo-audit.md)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

**VCaaS** — Empowering creators with ethical, traceable voice cloning technology.
