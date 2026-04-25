# Vigilens 🛡️

**AI-powered disaster video misinformation detection platform.**

Vigilens analyses disaster videos in real time to determine if they are authentic, misleading (recirculated with false context), AI-generated, or unverified. It uses a three-stage LangGraph agent pipeline: DeepFake Detector, Source Hunter, and Context Analyser — orchestrated by an LLM to produce a public-facing verdict with a credibility score and panic index.

---

## What is Vigilens?

During disasters, misinformation spreads faster than relief. Videos from old events get recirculated with false claims, AI-generated footage is passed off as real, and manipulated audio creates unnecessary panic. Vigilens is a verification platform built for disaster responders, journalists, and the public to quickly assess the authenticity of disaster videos.

---

## Architecture Overview

```
Next.js Frontend (port 3000)
      │  POST /api/analyze
      ▼
FastAPI Backend (port 8000)
      │  LangGraph StateGraph
      ▼
  [Preprocess Node]
   FFmpeg: Extract Keyframes + Audio
      │
      ├─────────────────────────────────────────────────────┐
      │                         │                           │
      ▼                         ▼                           ▼
[DeepFake Detector]    [Source Hunter]           [Context Analyser]
 Hive AI / DeepSafe    Google Vision / TinEye    Whisper + EasyOCR
 CrossEfficientViT     pHash / YouTube API       Vision LLM
      │                         │                           │
      └─────────────────────────┘───────────────────────────┘
                                │
                                ▼
                        [Orchestrator Node]
                        Groq / Ollama LLM
                        LangSmith Tracing
                                │
                                ▼
                        Final Verdict JSON
                        {verdict, credibilityScore, panicIndex, ...}
```

---

## Quick Start (Demo Mode — Zero Config)

```bash
# 1. Clone the repository
git clone https://github.com/your-org/vigilens.git
cd vigilens

# 2. Install frontend dependencies
cd frontend && npm install

# 3. Copy environment file (demo mode needs no API keys)
cp .env.local.example .env.local

# 4. Start the dev server
npm run dev

# 5. Open http://localhost:3000 — select a demo video and click Analyse
```

No API keys required in demo mode. Pre-computed results are shown.

---

## Environment Setup

All environment variables are documented in `frontend/.env.local.example` and `backend/.env.example`.

| Variable | Required | Default | Description |
|---|---|---|---|
| `NEXT_PUBLIC_INFERENCE_MODE` | No | `online` | `online` or `offline` |
| `NEXT_PUBLIC_APP_MODE` | No | `demo` | `demo` or `real` |
| `NEXT_PUBLIC_BACKEND_URL` | No | `http://localhost:8000` | Python backend URL |
| `GROQ_API_KEY` | Online mode | — | Groq API key for LLM |
| `HIVE_API_KEY` | Online mode | — | Hive AI for deepfake detection |
| `LANGSMITH_API_KEY` | Optional | — | LangSmith tracing |
| `GOOGLE_VISION_API_KEY` | Online mode | — | Reverse image search |
| `TINEYE_API_KEY` | Online mode | — | Image history search |
| `YOUTUBE_API_KEY` | Online mode | — | YouTube metadata |
| `OPENAI_API_KEY` | Online mode | — | Whisper API transcription |
| `DEEPSAFE_URL` | Offline mode | `http://localhost:8001` | Local DeepSafe API |
| `OLLAMA_BASE_URL` | Offline mode | `http://localhost:11434` | Local Ollama API |

---

## Online Mode Setup

Get these free API keys:

| Service | Free Tier | Link |
|---|---|---|
| **Groq** | 100K tokens/day | https://console.groq.com |
| **Hive AI** | 100 req/day | https://thehive.ai |
| **LangSmith** | Free | https://smith.langchain.com |
| **Google Vision** | 1000 req/month | https://console.cloud.google.com |
| **TinEye** | 150 req/month | https://services.tineye.com |
| **YouTube Data API** | Free with key | https://console.cloud.google.com |

Set in `frontend/.env.local`:
```env
NEXT_PUBLIC_INFERENCE_MODE=online
NEXT_PUBLIC_APP_MODE=real
GROQ_API_KEY=gsk_...
HIVE_API_KEY=...
```

---

## Offline Mode Setup

### 1. DeepSafe (Local Deepfake Detection)

```bash
git clone https://github.com/siddharthksah/DeepSafe
cd DeepSafe
docker compose up -d
curl http://localhost:8001/health
```

Models included:
- **CrossEfficientViT** — Video deepfake detection (primary)
- **UniversalFakeDetect** — Image AI generation detection

### 2. Ollama (Local LLM)

```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.3
ollama pull llava:13b
ollama pull llama3.1:8b
```

Minimum hardware:
- 16GB RAM (32GB recommended for llava:13b)
- NVIDIA GPU 8GB+ VRAM recommended
- CPU-only possible but slow (5-15 min/analysis)

### 3. Local Whisper

```bash
pip install openai-whisper
python -c "import whisper; m=whisper.load_model('medium'); print('Whisper ready')"
```

Model sizes: `tiny` (~1GB), `base` (~1GB), `small` (~2GB), `medium` (~5GB, recommended), `large` (~10GB)

---

## Switching Between Modes

| Scenario | `NEXT_PUBLIC_APP_MODE` | `NEXT_PUBLIC_INFERENCE_MODE` | Requirements |
|---|---|---|---|
| **Demo + Online** (default) | `demo` | `online` | None — zero config |
| **Demo + Offline** (hackathon, no internet) | `demo` | `offline` | None (demo data is static) |
| **Real + Online** (production) | `real` | `online` | Groq, Hive AI, Vision API keys |
| **Real + Offline** (air-gapped) | `real` | `offline` | Ollama + DeepSafe Docker + Whisper |

---

## LangGraph Agent Pipeline

### State Shape (`AgentState`)

```python
class AgentState(TypedDict):
    video_url: Optional[str]       # Input video URL
    video_path: Optional[str]      # Or local file path
    job_id: str                    # Unique job identifier
    keyframes: List[str]           # Extracted frame paths
    audio_path: Optional[str]      # Extracted audio path
    transcript: Optional[str]      # Whisper output
    ocr_text: Optional[str]        # On-screen text
    deepfake_result: AgentFinding  # DeepFake Detector output
    source_result: AgentFinding    # Source Hunter output
    context_result: AgentFinding   # Context Analyser output
    verdict: str                   # Final: real|misleading|ai-generated|unverified
    credibility_score: int         # 0-100
    panic_index: int               # 0-10
    summary: str                   # Public-facing explanation
    key_flags: List[str]           # Evidence flags
```

### Nodes

| Node | Input | Output | APIs Used |
|---|---|---|---|
| `preprocess` | video_url/path | keyframes[], audio_path | FFmpeg |
| `deepfake_detector` | keyframes[] | AgentFinding (score 0-100) | Hive AI / DeepSafe |
| `source_hunter` | keyframes[], video_url | AgentFinding (score 0-100) | Google Vision, TinEye, YouTube |
| `context_analyser` | keyframes[], audio_path | AgentFinding (score 0-100) | Whisper, EasyOCR, Groq vision |
| `orchestrator` | all AgentFindings | verdict, scores, summary | Groq / Ollama |

### LangSmith Tracing

Set `LANGSMITH_TRACING_V2=true` and `LANGSMITH_API_KEY`. All `@traceable` decorated functions and LangChain/LangGraph calls are automatically traced. View at https://smith.langchain.com/projects/vigilens.

---

## CI/CD Pipeline

| Workflow | Trigger | What It Does |
|---|---|---|
| `ci.yml` | Every push/PR | Biome lint, TypeScript check, Next.js build |
| `security.yml` | PRs + weekly | npm audit, dependency review, CodeQL |
| `python-checks.yml` | `backend/` changes | Ruff lint, mypy, pytest |
| `deploy.yml` | Main branch merge | Deploy frontend to Vercel |

---

## Contributing

### Adding a New Detection Agent

1. Create `backend/agents/nodes/your_agent.py` following the `AgentFinding` return pattern
2. Add the node to `backend/agents/graph.py` `parallel_analysis_node`
3. Add the agent to `AgentState` in `state.py`
4. Add the agent name to frontend `src/types/index.ts`
5. Add i18n key to all locale files in `src/i18n/locales/`

### Adding a New Language

1. Create `frontend/src/i18n/locales/{lang}.json` (copy from `en.json`)
2. Import and register in `frontend/src/i18n/config.ts`
3. Add the language code to the `languages` array in `Navbar.tsx`
4. Add `{lang}` to EasyOCR reader in `backend/agents/tools/ocr_tools.py`

### Adding a New Detection API

1. Add API key to `backend/.env.example` and `frontend/.env.local.example`
2. Add setting to `backend/config/settings.py`
3. Wrap API call in `try/except` with 5-second timeout
4. Integrate in the appropriate agent node file
5. Add to README Section "Online Mode Setup" table

---

## Deployment

### Frontend (Vercel)

```bash
cd frontend
npx vercel --prod
```

Set environment variables in Vercel dashboard.

### Backend (Railway / Render)

```bash
# Railway
railway up --service backend

# Render: connect GitHub repo, set build command:
# cd backend && pip install -r requirements.txt
# Set start command: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

### Full Local Stack (Docker)

```bash
# Online mode (no local AI models)
docker compose -f docker-compose.online.yml up

# Offline mode (local AI — requires GPU)
docker compose up
```

---

## License

MIT License — see [LICENSE](LICENSE)

Built for OpenLoop OL08 Hackathon.