# Vigilens: Engineering Deep Dive 🛡️

## 1. Executive Summary
Vigilens is a decentralized forensic intelligence platform designed to verify disaster-related video content. It employs a **Multi-Agent Orchestration** architecture to dissect digital media across four dimensions: **Synthetic Generation**, **Historical Provenance**, **Contextual Accuracy**, and **Geographical Validity**.

---

## 2. Core Architecture: The VIGILENS-OS Pipeline

### 2.1 Media Ingestion & Preprocessing
When a video is submitted, the system initiates a low-latency preprocessing routine:
- **Frame Sampling**: Uses FFmpeg to extract high-fidelity I-frames (keyframes). This reduces the token cost for vision LLMs by 95% while preserving critical visual evidence.
- **Audio Fingerprinting**: Extracts audio to check for AI-generated speech patterns (Whisper) and matches it against visual events (AV-sync).
- **Metadata Extraction**: Scrapes platform-specific metadata (YouTube/Twitter/Instagram) and checks for embedded camera EXIF tags.

### 2.2 LangGraph Orchestration
The heart of Vigilens is a directed acyclic graph (DAG) built with LangGraph:
1.  **State Management**: The `AgentState` object persists across all nodes, carrying keyframes, audio paths, and individual agent findings.
2.  **Concurrency**: The `parallel_analysis` node utilizes Python's `asyncio.gather` to launch the four detection agents simultaneously, ensuring analysis completes in under 20 seconds.
3.  **Traceability**: Every "thought" and API call is piped to **LangSmith**, providing a full audit trail for the verification verdict.

---

## 3. The Four Pillars of Verification

### Pillar I: Deepfake Detection (Synthetic Analysis)
- **Multi-Model Voting**: Combines **Google Vertex AI (Gemini 1.5 Pro)** for semantic analysis (e.g., "are the shadows physically possible?") with **Groq Vision (Llama 3.2)** for technical artifact detection.
- **Pixel-Variance Heuristic**: A custom algorithm that detects "unnatural" smoothing or noise patterns typical of AI upscalers and GAN generators.

### Pillar II: Source Hunter (Provenance Analysis)
- **Reverse Vision Search**: Uses Google Vision and TinEye to find the earliest known instance of the video's keyframes.
- **Temporal Verification**: Queries the **Wayback Machine** to see if the video URL was archived *before* the disaster event, a common indicator of recycled footage.

### Pillar III: Context Analyser (Environmental Analysis)
- **Meteorological Cross-Reference**: Queries **Open-Meteo** historical data. If a video shows a sunny flood in a region that had 100% cloud cover and rain on that day, it is flagged as `misleading`.
- **Disaster Database Matching**: Syncs with **GDACS** (Global Disaster Alert and Coordination System) to verify if an official disaster was recorded at the claimed coordinates.

### Pillar IV: Geolocation Hunter (Architectural Analysis)
- Uses vision LLMs to analyze **architecture, street signage, and flora**. It determines if the visual environment matches the claimed GPS coordinates or country.

---

## 4. The Vigilens Scoring Engine (ML)

The final verdict is not a "guess" by an LLM; it is a calculated result from a deterministic engine (`scoring_engine.py`).

### Scoring Formula:
The engine applies a weighted blend of binary constraints and model confidence scores:
- **Constraint Weights**: 60% of the score comes from hard checks (e.g., "Is EXIF present?").
- **Susceptibility Modifiers**: The engine is more "suspicious" of certain disasters (like Tsunamis) which are statistically more prone to AI generation for social media engagement.
- **Confidence Calibration**: Each agent provides a confidence percentage based on the quality of the input data (e.g., low-resolution video reduces confidence).

---

## 5. UI/UX: Design for High-Stakes Monitoring

The frontend is built for **speed and clarity**:
- **Bento Dashboard**: A modern, high-contrast interface that prioritizes the "Verdict Card" and "Panic Index".
- **Agent Progress**: Real-time status updates from each LangGraph node as they complete.
- **Global Bulletin**: A unified feed of verified disasters, serving as a "Source of Truth" for emergency responders.

---

## 6. Current Technical Status
- **Stack**: Next.js 14, FastAPI, LangGraph, Groq, Vertex AI.
- **Deployment**: Optimized for Vercel (Frontend) and Dockerized Cloud (Backend).
- **Architecture**: 100% Cloud-Optimized for zero-latency forensics.

---
*Vigilens: Engineering Truth in the Digital Age.*
