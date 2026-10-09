"""HTTP API for KubeSage."""

from fastapi import FastAPI
from app.engine import analyze_workload
from app.schemas import IncidentReport, WorkloadSnapshot

app = FastAPI(
    title="KubeSage Incident Intelligence API",
    description="Explainable analysis of Kubernetes workload health signals.",
    version="0.1.0",
)


@app.get("/", tags=["service"])
def root() -> dict[str, str]:
    return {"service": "kubesage", "version": app.version, "docs": "/docs"}


@app.get("/health", tags=["service"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready", tags=["service"])
def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.post("/analyze", response_model=IncidentReport, tags=["analysis"])
def analyze(snapshot: WorkloadSnapshot) -> IncidentReport:
    """Analyze one workload snapshot and return prioritized, explainable findings."""
    return analyze_workload(snapshot)
