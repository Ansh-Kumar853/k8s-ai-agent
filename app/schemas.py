"""Pydantic schemas used by the KubeSage API."""

from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class WorkloadSnapshot(BaseModel):
    """A normalized snapshot of a workload's current health signals."""

    model_config = ConfigDict(extra="forbid")

    cluster: str = Field(default="unknown-cluster", min_length=1, max_length=100)
    namespace: str = Field(default="default", min_length=1, max_length=100)
    workload: str = Field(min_length=1, max_length=120)
    desired_replicas: int = Field(ge=0, le=10000)
    available_replicas: int = Field(ge=0, le=10000)
    restart_count: int = Field(default=0, ge=0, le=1000000)
    cpu_percent: float = Field(default=0, ge=0, le=1000)
    memory_percent: float = Field(default=0, ge=0, le=1000)
    probe_failures: int = Field(default=0, ge=0, le=1000000)


class Finding(BaseModel):
    code: str
    severity: Literal["critical", "high", "medium", "low", "info"]
    title: str
    evidence: str
    recommendation: str
    score: int = Field(ge=0, le=100)


class IncidentReport(BaseModel):
    cluster: str
    namespace: str
    workload: str
    status: Literal["healthy", "degraded", "critical"]
    risk_score: int = Field(ge=0, le=100)
    summary: str
    findings: list[Finding]
    recommended_checks: list[str]
