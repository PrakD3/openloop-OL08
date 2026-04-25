"""
DeepFake Detector Agent — with custom ML scoring engine
========================================================
Constraint-based + ML-hybrid scoring.  Scores now reflect:
  - How many deepfake constraints pass
  - Raw API score (Hive / DeepSafe) blended in at 40%
  - Disaster-type susceptibility modifier
  - Per-model breakdown: CrossEfficientViT / UniversalFakeDetect / Hive AI
"""

import asyncio
import base64
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from langsmith import traceable

from ...config.settings import settings
from ...ml.scoring_engine import (
    DEEPFAKE_CONSTRAINTS,
    DeepfakeScoringResult,
    build_engine,
)
from ..state import AgentFinding, AgentState, ModelScore


@traceable(name="deepfake_detector")
async def deepfake_detector_node(state: AgentState) -> AgentFinding:
    """Route to online or offline deepfake detection based on INFERENCE_MODE."""
    start = time.time()

    disaster_type = state.get("disaster_type") or "unknown"
    job_id = state.get("job_id", "demo")
    engine = build_engine(job_id=job_id, disaster_type=disaster_type)

    if settings.inference_mode == "offline":
        result = await _deepsafe_detect(state, engine)
    elif settings.app_mode == "demo":
        result = _demo_result(engine)
    else:
        result = await _hive_detect(state, engine)

    result.duration_ms = int((time.time() - start) * 1000)
    return result


# ---------------------------------------------------------------------------
# Demo mode
# ---------------------------------------------------------------------------

def _demo_result(engine) -> AgentFinding:
    """Demo result using the scoring engine with typical authentic constraints."""
    constraints = {c: True for c in DEEPFAKE_CONSTRAINTS}
    # Simulate a mostly-authentic video with minor uncertainty
    constraints["no_gan_artifacts"] = True
    constraints["consistent_lighting"] = True
    constraints["av_sync_intact"] = True
    constraints["natural_motion_blur"] = True
    constraints["temporal_consistency"] = True
    constraints["natural_pixel_variance"] = True
    constraints["no_synthetic_audio"] = True

    scored: DeepfakeScoringResult = engine.score_deepfake(constraints, api_fake_score=4.5)

    model_scores = _convert_model_scores(scored.model_scores)
    findings = [
        f"No facial manipulation detected ({scored.constraints_satisfied}/{scored.total_constraints} checks passed)",
        "Consistent lighting and shadow patterns",
        "Audio-visual sync verified",
        f"CrossEfficientViT: {scored.model_scores[0].authentic_pct:.1f}% authentic",
        f"UniversalFakeDetect: {scored.model_scores[1].authentic_pct:.1f}% authentic",
    ]

    return AgentFinding(
        agent_id="deepfake-detector",
        agent_name="DeepFake Detector",
        status="done",
        score=round(scored.fake_score, 1),
        findings=findings,
        detail=f"Demo: {scored.constraints_satisfied}/{scored.total_constraints} constraints passed. Fake score: {scored.fake_score:.1f}%",
        constraints_satisfied=scored.constraints_satisfied,
        total_constraints=scored.total_constraints,
        constraint_details=scored.constraint_details,
        model_scores=model_scores,
    )


# ---------------------------------------------------------------------------
# Hive AI (online)
# ---------------------------------------------------------------------------

async def _hive_detect(state: AgentState, engine) -> AgentFinding:
    keyframes: List[str] = state.get("keyframes", [])
    api_scores: List[float] = []
    raw_findings: List[str] = []

    if keyframes and settings.hive_api_key:
        async with httpx.AsyncClient(timeout=10.0) as client:
            for frame_path in keyframes[:5]:
                try:
                    with open(frame_path, "rb") as f:
                        files = {"media": f}
                        response = await client.post(
                            "https://api.thehive.ai/api/v2/task/sync",
                            headers={"token": settings.hive_api_key},
                            files=files,
                        )
                    if response.status_code == 200:
                        data = response.json()
                        classes = (
                            data.get("status", [{}])[0]
                            .get("response", {})
                            .get("output", [{}])[0]
                            .get("classes", [])
                        )
                        for cls in classes:
                            if cls.get("class") == "ai_generated":
                                api_scores.append(float(cls.get("score", 0)) * 100)
                except Exception as exc:
                    raw_findings.append(f"Frame analysis error: {exc}")

    api_fake_score = max(api_scores) if api_scores else None

    # Build constraint values from what we know
    constraints = _infer_deepfake_constraints(state, api_fake_score)
    scored: DeepfakeScoringResult = engine.score_deepfake(constraints, api_fake_score=api_fake_score)

    model_scores = _convert_model_scores(scored.model_scores)
    findings = raw_findings + _summarise_constraints(scored.constraint_details)
    if api_fake_score is not None:
        findings.insert(0, f"Hive AI raw fake confidence: {api_fake_score:.1f}%")

    return AgentFinding(
        agent_id="deepfake-detector",
        agent_name="DeepFake Detector",
        status="done",
        score=round(scored.fake_score, 1),
        findings=findings or ["No deepfake signals detected"],
        detail=f"{scored.constraints_satisfied}/{scored.total_constraints} constraints passed. Fake score: {scored.fake_score:.1f}%",
        constraints_satisfied=scored.constraints_satisfied,
        total_constraints=scored.total_constraints,
        constraint_details=scored.constraint_details,
        model_scores=model_scores,
    )


# ---------------------------------------------------------------------------
# DeepSafe (offline)
# ---------------------------------------------------------------------------

async def _deepsafe_detect(state: AgentState, engine) -> AgentFinding:
    keyframes: List[str] = state.get("keyframes", [])
    api_scores: List[float] = []
    raw_findings: List[str] = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for frame_path in keyframes[:5]:
            try:
                with open(frame_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode()
                response = await client.post(
                    f"{settings.deepsafe_url}/api/detect",
                    json={"image_base64": img_b64, "model": "CrossEfficientViT"},
                )
                if response.status_code == 200:
                    data = response.json()
                    confidence = float(data.get("confidence", 0)) * 100
                    api_scores.append(confidence)
                    is_fake = data.get("is_fake", False)
                    raw_findings.append(
                        f"Frame: {'FAKE' if is_fake else 'AUTHENTIC'} ({confidence:.1f}% confidence)"
                    )
            except Exception as exc:
                raw_findings.append(f"DeepSafe error: {exc}")

    api_fake_score = max(api_scores) if api_scores else None
    constraints = _infer_deepfake_constraints(state, api_fake_score)
    scored: DeepfakeScoringResult = engine.score_deepfake(constraints, api_fake_score=api_fake_score)
    model_scores = _convert_model_scores(scored.model_scores)

    findings = raw_findings + _summarise_constraints(scored.constraint_details)

    return AgentFinding(
        agent_id="deepfake-detector",
        agent_name="DeepFake Detector",
        status="done",
        score=round(scored.fake_score, 1),
        findings=findings or ["DeepSafe API unavailable — heuristic used"],
        detail=f"DeepSafe: {scored.constraints_satisfied}/{scored.total_constraints} constraints passed. Fake: {scored.fake_score:.1f}%",
        constraints_satisfied=scored.constraints_satisfied,
        total_constraints=scored.total_constraints,
        constraint_details=scored.constraint_details,
        model_scores=model_scores,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _infer_deepfake_constraints(state: AgentState, api_fake_score: Optional[float]) -> Dict[str, bool]:
    """
    Infer binary constraint values from available signals.
    When an API score is available it anchors the key constraints.
    """
    # Default: benefit of the doubt
    c: Dict[str, bool] = {k: True for k in DEEPFAKE_CONSTRAINTS}

    if api_fake_score is not None:
        # High fake score → flip several constraints to False
        if api_fake_score > 70:
            c["no_gan_artifacts"] = False
            c["consistent_lighting"] = False
            c["temporal_consistency"] = False
        elif api_fake_score > 40:
            c["no_gan_artifacts"] = False
            c["temporal_consistency"] = False

        if api_fake_score > 60:
            c["no_synthetic_audio"] = False
        if api_fake_score > 80:
            c["natural_pixel_variance"] = False
            c["natural_motion_blur"] = False

    # OCR/transcript presence is a weak positive signal
    if not state.get("transcript") and not state.get("ocr_text"):
        c["av_sync_intact"] = False  # can't verify without transcript

    return c


def _convert_model_scores(ml_scores) -> List[ModelScore]:
    return [
        ModelScore(
            model_name=m.model_name,
            authentic_pct=m.authentic_pct,
            fake_pct=m.fake_pct,
            confidence=m.confidence,
        )
        for m in ml_scores
    ]


def _summarise_constraints(details: Dict[str, bool]) -> List[str]:
    passed = [k.replace("_", " ").title() for k, v in details.items() if v]
    failed = [k.replace("_", " ").title() for k, v in details.items() if not v]
    findings = []
    if passed:
        findings.append(f"Passed checks: {', '.join(passed[:4])}")
    if failed:
        findings.append(f"Failed checks: {', '.join(failed[:3])}")
    return findings
