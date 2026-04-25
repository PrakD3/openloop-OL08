"""Pydantic request/response models for the Vigilens API."""

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    video_url: Optional[str] = None
    video_path: Optional[str] = None
    claimed_location: Optional[str] = None


class ModelScoreResponse(BaseModel):
    model_name: str
    authentic_pct: float
    fake_pct: float
    confidence: float


class ConstraintResult(BaseModel):
    name: str
    passed: bool


class AgentFindingResponse(BaseModel):
    agent_id: str
    agent_name: str
    status: Literal["idle", "running", "done", "error"]
    score: Optional[float] = None
    findings: List[str] = []
    detail: Optional[str] = None
    duration_ms: Optional[int] = None
    constraints_satisfied: Optional[int] = None
    total_constraints: Optional[int] = None
    constraint_details: Dict[str, bool] = {}
    model_scores: List[ModelScoreResponse] = []   # deepfake agent only


class SOSRegion(BaseModel):
    lat: float
    lng: float
    radius_km: float
    center_name: str
    disaster_type: str
    panic_index: int
    color: str
    sos_active: bool


class AnalyzeResponse(BaseModel):
    job_id: str
    verdict: Literal["real", "misleading", "ai-generated", "unverified"]
    credibility_score: int = Field(ge=0, le=100)
    panic_index: int = Field(ge=0, le=10)
    summary: str
    disaster_type: str = "unknown"
    source_origin: Optional[str] = None
    original_date: Optional[str] = None
    claimed_location: Optional[str] = None
    actual_location: Optional[str] = None
    key_flags: List[str] = []
    agents: List[AgentFindingResponse] = []
    sos_region: Optional[SOSRegion] = None


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
