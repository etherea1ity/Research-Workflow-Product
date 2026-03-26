from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ArtifactType(str, Enum):
    RESEARCH_BRIEF = "research_brief"
    COMPETITOR_MATRIX = "competitor_matrix"
    MVP_SPEC = "mvp_spec"
    ISSUE_BUNDLE = "issue_bundle"


class SourceInput(BaseModel):
    kind: str = Field(description="One of url, github_repo, local_doc, note.")
    value: str


class RunCreateRequest(BaseModel):
    idea: str = Field(min_length=4)
    goals: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    desired_artifacts: list[ArtifactType] = Field(
        default_factory=lambda: [
            ArtifactType.RESEARCH_BRIEF,
            ArtifactType.COMPETITOR_MATRIX,
            ArtifactType.MVP_SPEC,
            ArtifactType.ISSUE_BUNDLE,
        ]
    )
    optional_sources: list[SourceInput] = Field(default_factory=list)


class EvidenceItem(BaseModel):
    evidence_id: str
    skill: str
    title: str
    summary: str
    source: str
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArtifactRecord(BaseModel):
    artifact_type: ArtifactType
    title: str
    content: dict[str, Any]
    evidence_ids: list[str] = Field(default_factory=list)


class TraceRecord(BaseModel):
    stage: str
    started_at: datetime
    finished_at: datetime
    duration_ms: float
    status: str
    details: dict[str, Any] = Field(default_factory=dict)


class RunMetrics(BaseModel):
    coverage_score: float = 0.0
    evidence_support_rate: float = 0.0
    actionability_score: float = 0.0
    total_token_usage: int = 0
    latency_ms: float = 0.0
    user_edit_distance: float = 0.0


class RunRecord(BaseModel):
    run_id: str
    status: str
    current_stage: str
    created_at: datetime
    updated_at: datetime
    request: RunCreateRequest
    stage_history: list[str] = Field(default_factory=list)
    project_profile: dict[str, Any] = Field(default_factory=dict)
    task_state: dict[str, Any] = Field(default_factory=dict)
    scratchpad: dict[str, Any] = Field(default_factory=dict)
    evidence_store: list[EvidenceItem] = Field(default_factory=list)
    artifacts: list[ArtifactRecord] = Field(default_factory=list)
    trace: list[TraceRecord] = Field(default_factory=list)
    metrics: RunMetrics = Field(default_factory=RunMetrics)
    evaluation_plan: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class RunCreatedResponse(BaseModel):
    run_id: str
    current_stage: str
    artifact_refs: list[ArtifactType]


class RunDetailResponse(BaseModel):
    run_id: str
    status: str
    current_stage: str
    stage_history: list[str]
    evidence_summary: list[EvidenceItem]
    artifact_summary: list[ArtifactRecord]
    trace: list[TraceRecord]
    metrics: RunMetrics
    task_state: dict[str, Any]
    evaluation_plan: dict[str, Any]
    error: str | None = None
