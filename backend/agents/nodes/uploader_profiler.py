"""Uploader profiler agent node — analyzes account credibility and upload metadata."""

import json
import logging

from agents.state import AgentState
from agents.tools.metadata_extractor import extract_platform_metadata, extract_reddit_metadata
from config.settings import settings

logger = logging.getLogger(__name__)

UPLOADER_ANALYSIS_PROMPT = """
You are a forensic media analyst specializing in source credibility for disaster footage verification.

Analyze the following metadata about a video and its uploader. Provide a structured credibility assessment.

PLATFORM METADATA:
{platform_metadata}

REDDIT-SPECIFIC DATA (if applicable):
{reddit_metadata}

OCR TEXT FROM VIDEO (channel names, watermarks visible in frames):
{ocr_text}

Your task:
1. Assess uploader/account legitimacy (account age, follower count, karma, posting history signals)
2. Identify any temporal inconsistencies (upload date vs claimed event date)
3. Flag suspicious signals: brand-new account, no follower history, odd posting time, cross-post chains
4. Identify trust signals: verified account, established channel, consistent topic history
5. Cross-reference OCR channel names with the uploader to check for impersonation

Respond ONLY with valid JSON matching this schema exactly:
{{
  "trust_score": <integer 0-100>,
  "uploader_summary": "<2-3 sentence plain English summary of who uploaded this and their credibility>",
  "account_age_signal": "<'new_account' | 'established' | 'unknown'>",
  "red_flags": ["<flag1>", "<flag2>"],
  "trust_signals": ["<signal1>", "<signal2>"],
  "temporal_note": "<observation about upload timing relative to any event claims, or null>",
  "platform_notes": "<any platform-specific observations>"
}}
"""


async def run(state: AgentState) -> AgentState:
    logger.info(f"[UPLOADER_PROFILER] Starting for job {state.get('job_id', '?')}")

    video_url = state.get("video_url", "")
    ocr_text = state.get("ocr_text", "") or ""

    # Extract metadata
    platform_meta = await extract_platform_metadata(video_url)
    reddit_meta = await extract_reddit_metadata(video_url)

    # Store raw metadata in state
    state["platform_metadata"] = platform_meta
    state["reddit_metadata"] = reddit_meta

    # Build uploader intelligence via Groq
    client = None
    try:
        from groq import AsyncGroq

        client = AsyncGroq(api_key=settings.groq_api_key)

        prompt = UPLOADER_ANALYSIS_PROMPT.format(
            platform_metadata=json.dumps(platform_meta, indent=2, default=str),
            reddit_metadata=json.dumps(reddit_meta, indent=2, default=str)
            if reddit_meta
            else "N/A",
            ocr_text=ocr_text[:400] if ocr_text else "Not available",
        )

        response = await client.chat.completions.create(
            model=settings.groq_orchestrator_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content
        uploader_intelligence = json.loads(raw)
        logger.info(f"[UPLOADER_PROFILER] Trust score: {uploader_intelligence.get('trust_score')}")

    except Exception as e:
        logger.error(f"[UPLOADER_PROFILER] Groq analysis failed: {e}")
        uploader_intelligence = {
            "trust_score": 50,
            "uploader_summary": "Uploader analysis unavailable.",
            "account_age_signal": "unknown",
            "red_flags": [],
            "trust_signals": [],
            "temporal_note": None,
            "platform_notes": f"Analysis error: {str(e)[:80]}",
        }

    state["uploader_intelligence"] = uploader_intelligence

    # Fetch and analyse comments
    try:
        from agents.tools.comment_fetcher import (
            analyse_comments_for_intelligence,
            fetch_top_comments,
        )

        comments = await fetch_top_comments(video_url, limit=15)
        comment_intelligence = None
        if comments and client:
            comment_intelligence = await analyse_comments_for_intelligence(
                comments=comments,
                groq_client=client,
                model=settings.groq_orchestrator_model,
            )
            logger.info(
                f"[UPLOADER_PROFILER] Comment analysis: {comment_intelligence.get('community_verdict') if comment_intelligence else 'failed'}"
            )

        state["comments_raw"] = comments
        state["comment_intelligence"] = comment_intelligence
    except Exception as e:
        logger.error(f"[UPLOADER_PROFILER] Comment fetch failed: {e}")
        state["comments_raw"] = []
        state["comment_intelligence"] = None

    return state
