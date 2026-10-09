from app.engine import analyze_workload
from app.schemas import WorkloadSnapshot


def make_snapshot(**overrides):
    data = {
        "cluster": "test-cluster",
        "namespace": "payments",
        "workload": "checkout-api",
        "desired_replicas": 3,
        "available_replicas": 3,
        "restart_count": 0,
        "cpu_percent": 25,
        "memory_percent": 40,
        "probe_failures": 0,
    }
    data.update(overrides)
    return WorkloadSnapshot(**data)


def test_healthy_snapshot_has_no_findings():
    report = analyze_workload(make_snapshot())
    assert report.status == "healthy"
    assert report.risk_score == 0
    assert report.findings == []


def test_replica_shortfall_is_reported():
    report = analyze_workload(make_snapshot(available_replicas=1))
    assert report.status in {"degraded", "critical"}
    assert any(f.code == "REPLICA_SHORTFALL" for f in report.findings)


def test_multiple_signals_are_prioritized():
    report = analyze_workload(make_snapshot(
        available_replicas=1,
        restart_count=14,
        cpu_percent=96,
        memory_percent=99,
        probe_failures=6,
    ))
    assert report.status == "critical"
    assert report.risk_score <= 100
    assert report.findings[0].score >= report.findings[-1].score
    assert len(report.recommended_checks) <= 3


def test_invalid_percentages_are_rejected():
    try:
        make_snapshot(cpu_percent=1200)
    except ValueError:
        return
    raise AssertionError("Expected validation to reject an out-of-range CPU percentage")
