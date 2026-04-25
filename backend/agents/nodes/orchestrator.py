"""
Orchestrator Node — plain-English summaries + SOS region
=========================================================
Changes vs original:
- Extracts disaster_type from context_analyser detail string
- Uses the custom scoring engine to compute final credibility / panic / verdict
- Prompts the LLM for plain-English summary (no jargon) in black-and-white style
- Calls the SOS engine when a genuine disaster is confirmed
"""

import json
import re
import time
from dataclasses import asdict
from typing import Any, Dict, Optional

from langsmith import traceable

from ...config.settings import get_llm, settings
from ...ml.disaster_classifier import classify_disaster
from ...ml.scoring_engine import build_engine
from ...ml.sos_engine import get_sos_region
from ..state import AgentFinding, AgentState
from ...api.job_store import update_progress

# ---------------------------------------------------------------------------
# LLM Prompt — plain English, no jargon
# ---------------------------------------------------------------------------

ORCHESTRATOR_PROMPT = """
You are a disaster video verification assistant writing for the general public.
Three AI agents have analysed a video. Summarise what they found in plain English.

AGENT RESULTS:
{agent_results_json}

DISASTER TYPE DETECTED: {disaster_type}

Rules for the verdict field:
- "real"          → credibility_score >= 68 AND deepfake fake_score <= 25
- "misleading"    → real footage but shown with wrong location, date, or context
- "ai-generated"  → deepfake fake_score >= 68
- "unverified"    → not enough evidence to be certain either way

Write the summary as if explaining to a person with no technical background.
Use short sentences. Avoid words like: deepfake, GAN, pixel variance, CrossEfficientViT,
heuristic, LLM, OCR, pHash. Instead say: "this video appears real/fake", "the source is trusted/unknown",
"the location matches/does not match", etc.

Respond ONLY with valid JSON (no markdown fences):
{{
  "verdict": "real" | "misleading" | "ai-generated" | "unverified",
  "credibility_score": <0-100 integer>,
  "panic_index": <0-10 integer>,
  "summary": "<2-4 plain English sentences that a regular person can understand>",
  "source_origin": "<earliest known URL or null>",
  "original_date": "<YYYY-MM-DD or null>",
  "claimed_location": "<claimed location or null>",
  "actual_location": "<confirmed location if different, or null>",
  "key_flags": ["<short plain English flag>", ...]
}}
"""


@traceable(name="orchestrator")
async def orchestrator_node(state: AgentState) -> Dict:
    """Compile final verdict from all agent findings."""
    job_id = state.get("job_id", "unknown")
    update_progress(job_id, 0.85, "orchestrator_starting")

    if settings.app_mode == "demo":
        return await _demo_verdict(state)

    deepfake = state.get("deepfake_result")
    source   = state.get("source_result")
    context  = state.get("context_result")

    # Extract disaster_type embedded by context_analyser
    disaster_type = _extract_disaster_type(context) or classify_disaster(
        video_url=state.get("video_url")
    )

    agent_results = {
        "deepfake_detector": _finding_to_dict(deepfake),
        "source_hunter":     _finding_to_dict(source),
        "context_analyser":  _finding_to_dict(context),
    }

    prompt = ORCHESTRATOR_PROMPT.format(
        agent_results_json=json.dumps(agent_results, indent=2),
        disaster_type=disaster_type,
    )

    llm_verdict: Optional[str] = None
    llm_credibility: Optional[int] = None
    verdict_data: Dict = {}

    try:
        llm = get_llm()
        response = llm.invoke(prompt)
        raw = response.content if hasattr(response, "content") else str(response)
        raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        verdict_data = json.loads(raw)
        llm_verdict = verdict_data.get("verdict")
        llm_credibility = int(verdict_data.get("credibility_score", 50))
    except Exception as exc:
        verdict_data = {
            "verdict": None,
            "credibility_score": None,
            "panic_index": None,
            "summary": _fallback_summary(deepfake, source, context, disaster_type),
            "source_origin": None,
            "original_date": None,
            "claimed_location": state.get("claimed_location"),
            "actual_location": None,
            "key_flags": ["Automated check completed — manual review recommended"],
        }

    # Use scoring engine for final authoritative numbers
    job_id = state.get("job_id", "")
    engine = build_engine(job_id=job_id, disaster_type=disaster_type)

    # Build stub scoring objects from agent findings
    from ...ml.scoring_engine import (
        DeepfakeScoringResult, SourceScoringResult, ContextScoringResult,
        DEEPFAKE_CONSTRAINTS, SOURCE_CONSTRAINTS, CONTEXT_CONSTRAINTS,
    )

    def _stub_deepfake():
        d = deepfake
        if d and hasattr(d, "score") and d.score is not None:
            fake = float(d.score)
        else:
            fake = 50.0
        return DeepfakeScoringResult(
            fake_score=fake, authentic_score=100 - fake,
            constraints_satisfied=getattr(d, "constraints_satisfied", None) or int(len(DEEPFAKE_CONSTRAINTS) * 0.6),
            total_constraints=len(DEEPFAKE_CONSTRAINTS),
        )

    def _stub_source():
        s = source
        if s and hasattr(s, "score") and s.score is not None:
            auth = float(s.score)
        else:
            auth = 50.0
        return SourceScoringResult(
            authenticity_score=auth,
            constraints_satisfied=getattr(s, "constraints_satisfied", None) or int(len(SOURCE_CONSTRAINTS) * 0.5),
            total_constraints=len(SOURCE_CONSTRAINTS),
        )

    def _stub_context():
        c = context
        if c and hasattr(c, "score") and c.score is not None:
            match = float(c.score)
        else:
            match = 50.0
        return ContextScoringResult(
            match_score=match,
            constraints_satisfied=getattr(c, "constraints_satisfied", None) or int(len(CONTEXT_CONSTRAINTS) * 0.5),
            total_constraints=len(CONTEXT_CONSTRAINTS),
        )

    final_scores = engine.compute_final_verdict(
        deepfake=_stub_deepfake(),
        source=_stub_source(),
        context=_stub_context(),
        llm_credibility=llm_credibility,
        llm_verdict=llm_verdict,
    )

    # SOS region: only for confirmed real disasters with significant panic
    sos_region = None
    location = (
        verdict_data.get("actual_location")
        or verdict_data.get("claimed_location")
        or state.get("claimed_location")
        or ""
    )
    if final_scores.verdict == "real" and final_scores.panic_index >= 5 and location:
        sos_region = await get_sos_region(
            location=location,
            disaster_type=disaster_type,
            panic_index=final_scores.panic_index,
        )

    summary = verdict_data.get("summary") or _fallback_summary(deepfake, source, context, disaster_type)

    update_progress(job_id, 0.90, "orchestrator_done")

    return {
        **state,
        "verdict":          final_scores.verdict,
        "credibility_score": final_scores.credibility_score,
        "panic_index":      final_scores.panic_index,
        "summary":          summary,
        "disaster_type":    disaster_type,
        "source_origin":    verdict_data.get("source_origin"),
        "original_date":    verdict_data.get("original_date"),
        "claimed_location": verdict_data.get("claimed_location") or state.get("claimed_location"),
        "actual_location":  verdict_data.get("actual_location"),
        "key_flags":        verdict_data.get("key_flags", []),
        "sos_region":       sos_region,
    }


# ---------------------------------------------------------------------------
# Demo mode
# ---------------------------------------------------------------------------

async def _demo_verdict(state: AgentState) -> Dict:
    """Demo mode: uses scoring engine with representative constraint counts."""
    deepfake = state.get("deepfake_result")
    source   = state.get("source_result")
    context  = state.get("context_result")

    disaster_type = _extract_disaster_type(context) or classify_disaster(
        video_url=state.get("video_url")
    ) or "flood"

    job_id = state.get("job_id", "demo")
    engine = build_engine(job_id=job_id, disaster_type=disaster_type)

    from ...ml.scoring_engine import (
        DeepfakeScoringResult, SourceScoringResult, ContextScoringResult,
        DEEPFAKE_CONSTRAINTS, SOURCE_CONSTRAINTS, CONTEXT_CONSTRAINTS,
    )

    d_fake = float(deepfake.score) if deepfake and deepfake.score is not None else 5.0
    s_auth = float(source.score)  if source  and source.score  is not None else 85.0
    c_match = float(context.score) if context and context.score is not None else 88.0

    df = DeepfakeScoringResult(fake_score=d_fake, authentic_score=100 - d_fake,
                               constraints_satisfied=6, total_constraints=7)
    sr = SourceScoringResult(authenticity_score=s_auth, constraints_satisfied=5, total_constraints=6)
    cr = ContextScoringResult(match_score=c_match, constraints_satisfied=5, total_constraints=6)

    final_scores = engine.compute_final_verdict(df, sr, cr)

    # Build a plain-English demo summary
    summary = _build_plain_summary(final_scores.verdict, disaster_type, s_auth, d_fake)

    # SOS for demo if verdict is real
    sos_region = None
    location = state.get("claimed_location") or "Chennai, India"
    if final_scores.verdict == "real" and final_scores.panic_index >= 5:
        sos_region = await get_sos_region(location, disaster_type, final_scores.panic_index)

    return {
        **state,
        "verdict":          final_scores.verdict,
        "credibility_score": final_scores.credibility_score,
        "panic_index":      final_scores.panic_index,
        "summary":          summary,
        "disaster_type":    disaster_type,
        "source_origin":    None,
        "original_date":    None,
        "claimed_location": state.get("claimed_location"),
        "actual_location":  None,
        "key_flags":        ["Demo mode active"],
        "sos_region":       sos_region,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _finding_to_dict(finding: Any) -> Dict:
    if finding is None:
        return {"status": "not_run"}
    if hasattr(finding, "__dataclass_fields__"):
        d = asdict(finding)
        # Remove non-serialisable nested objects if any
        return d
    return {}


def _extract_disaster_type(context: Optional[AgentFinding]) -> Optional[str]:
    """Extract disaster_type embedded in context_analyser detail string."""
    if context and context.detail:
        m = re.search(r"disaster_type:(\w+)", context.detail)
        if m:
            return m.group(1)
    return None


def _build_plain_summary(verdict: str, disaster_type: str, source_score: float, fake_score: float) -> str:
    dtype = disaster_type.capitalize() if disaster_type != "unknown" else "Disaster"
    if verdict == "real":
        return (
            f"This appears to be genuine {dtype.lower()} footage. "
            f"The source checks out and there are no signs of tampering. "
            f"The location and conditions shown match what was reported at the time."
        )
    elif verdict == "ai-generated":
        return (
            f"This video is very likely generated by AI — it is not real footage. "
            f"Multiple checks found digital artifacts that are not present in authentic videos. "
            f"Do not share this video as evidence of a real event."
        )
    elif verdict == "misleading":
        return (
            f"This video shows real footage, but it appears to have been shared with incorrect information. "
            f"The clip may be from a different time, location, or event than what is being claimed. "
            f"Verify the original source before sharing."
        )
    else:
        return (
            f"We could not fully verify this video. "
            f"Some checks passed but there was not enough evidence to confirm or deny its authenticity. "
            f"Treat this content with caution until more information is available."
        )


def _fallback_summary(deepfake, source, context, disaster_type: str) -> str:
    """Generate a plain-English summary without LLM when it fails."""
    d_fake = float(deepfake.score) if deepfake and deepfake.score is not None else 50.0
    s_auth = float(source.score)  if source  and source.score  is not None else 50.0

    if d_fake > 70:
        verdict_hint = "ai-generated"
    elif s_auth > 70 and d_fake < 20:
        verdict_hint = "real"
    elif s_auth < 30:
        verdict_hint = "misleading"
    else:
        verdict_hint = "unverified"

    return _build_plain_summary(verdict_hint, disaster_type, s_auth, d_fake)
