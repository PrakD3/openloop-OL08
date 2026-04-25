# Vigilens — Future Plans & Roadmap

This document outlines the planned features and enhancements for **Vigilens** following the initial MVP build.

## 1. Notification & Alerting System
Real-time alerting is critical for disaster response. We aim to implement a system that pushes verified information to responders the moment it is analyzed.

### Option A: Simple Push Alerts (The "Fast" Path)
Integrate direct webhooks to common messaging platforms.
- **Triggers**: 
  - `panic_index > 7`: Immediate high-priority alert.
  - `verdict == 'misleading'`: Alert to debunk recirculated misinformation.
  - `credibility_score < 30`: Alert for potential AI-generated/deepfake threats.
- **Integrations**: Telegram Bot API, Slack Webhooks, Discord Webhooks.

### Option B: OpenClaw Integration (The "Agentic" Path)
Integrate Vigilens as a skill within the **OpenClaw** autonomous agent framework.
- **Interactive Analysis**: Users can send video links directly to a WhatsApp/Telegram bot powered by OpenClaw + Vigilens.
- **Queryable Database**: Responders can ask the agent: *"Has there been any verified footage from the northern district in the last hour?"*
- **Proactive Monitoring**: Set OpenClaw to monitor specific social media tags and automatically run them through the Vigilens pipeline.

## 2. Multi-Modal Expansion
- **Live Stream Analysis**: Extend the pipeline to analyze RTMP/HLS live streams in chunks rather than just uploaded files.
- **Satellite Imagery Cross-Reference**: Use Vision LLMs to compare video landmarks with recent satellite imagery to verify geolocation claims.

## 3. Decentralized Verification (Web3)
- **Attestation on Chain**: Store the final verdict and its cryptographic hash on a decentralized ledger (e.g., Sign Protocol or Arweave) to create a permanent, tamper-proof record of truth.
- **Community Fact-Checking**: Allow trusted journalists to "stake" their reputation on a verdict.

## 4. Enhanced UI/UX
- **Geospatial Dashboard**: A real-time map showing verified vs. unverified incidents globally.
- **Deepfake Heatmap**: Visual overlay on videos showing exactly which parts of a face or background were flagged as AI-generated.
