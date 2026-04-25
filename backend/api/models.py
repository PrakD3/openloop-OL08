"""Pydantic request/response models for the Vigilens API."""

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    video_url: Optional[str] = None
    video_path: Optional[str] = None
    claimed_location: Optional[str] = None


class AgentFindingResponse(BaseModel):
    agent_id: str
    agent_name: str
    status: Literal["idle", "running", "done", "error"]
    score: Optional[float] = None
    findings: List[str] = []
    detail: Optional[str] = None
    duration_ms: Optional[int] = None


class AnalyzeResponse(BaseModel):
    job_id: str
    verdict: Literal["real", "misleading", "ai-generated", "unverified"]
    credibility_score: int = Field(ge=0, le=100)
    panic_index: int = Field(ge=0, le=10)
    summary: str
    source_origin: Optional[str] = None
    original_date: Optional[str] = None
    claimed_location: Optional[str] = None
    actual_location: Optional[str] = None
    key_flags: List[str] = []
    agents: List[AgentFindingResponse] = []


class JobStatusResponse(BaseModel):
    job_id: str
    status: Literal["queued", "processing", "done", "error"]
    progress: int = Field(ge=0, le=100)
    result: Optional[AnalyzeResponse] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    mode: str
    app_mode: str
    version: str = "0.1.0"
