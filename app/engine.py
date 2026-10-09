"""Deterministic, explainable workload analysis rules."""

from app.schemas import Finding, IncidentReport, WorkloadSnapshot


def analyze_workload(snapshot: WorkloadSnapshot) -> IncidentReport:
    findings: list[Finding] = []

    unavailable = max(snapshot.desired_replicas - snapshot.available_replicas, 0)
    if snapshot.desired_replicas > 0 and unavailable > 0:
        ratio = unavailable / snapshot.desired_replicas
        severity = "critical" if ratio >= 0.5 else "high" if ratio >= 0.25 else "medium"
        findings.append(Finding(
            code="REPLICA_SHORTFALL",
            severity=severity,
            title="Workload has fewer available replicas than desired",
            evidence=f"{snapshot.available_replicas}/{snapshot.desired_replicas} replicas are available ({unavailable} unavailable).",
            recommendation="Inspect pod events and scheduling constraints; check image pulls, resource pressure, readiness probes, and recent rollout changes.",
            score=min(100, int(45 + ratio * 55)),
        ))

    if snapshot.restart_count >= 10:
        findings.append(Finding(
            code="RESTART_SPIKE", severity="high",
            title="Container restart count is elevated",
            evidence=f"The reported restart count is {snapshot.restart_count}.",
            recommendation="Check the previous container logs and pod events; verify memory limits, startup behavior, and dependency availability.",
            score=min(95, 55 + snapshot.restart_count),
        ))
    elif snapshot.restart_count >= 3:
        findings.append(Finding(
            code="RESTARTS_OBSERVED", severity="medium",
            title="Repeated container restarts detected",
            evidence=f"The reported restart count is {snapshot.restart_count}.",
            recommendation="Review previous container logs and Kubernetes events to identify the exit reason.",
            score=min(70, 30 + snapshot.restart_count * 3),
        ))

    if snapshot.cpu_percent >= 90:
        findings.append(Finding(
            code="CPU_PRESSURE", severity="high" if snapshot.cpu_percent >= 97 else "medium",
            title="CPU utilization is near its configured ceiling",
            evidence=f"Reported CPU utilization is {snapshot.cpu_percent:.1f}%.",
            recommendation="Check throttling and request/limit settings; profile hot paths and compare utilization across replicas before scaling.",
            score=min(95, int(snapshot.cpu_percent)),
        ))

    if snapshot.memory_percent >= 90:
        findings.append(Finding(
            code="MEMORY_PRESSURE", severity="critical" if snapshot.memory_percent >= 98 else "high",
            title="Memory utilization is dangerously high",
            evidence=f"Reported memory utilization is {snapshot.memory_percent:.1f}%.",
            recommendation="Inspect working-set trends and OOMKilled events; check for leaks and confirm memory requests and limits match observed use.",
            score=min(100, int(snapshot.memory_percent)),
        ))

    if snapshot.probe_failures > 0:
        severity = "high" if snapshot.probe_failures >= 5 else "medium"
        findings.append(Finding(
            code="PROBE_FAILURES", severity=severity,
            title="Health probe failures were reported",
            evidence=f"The snapshot includes {snapshot.probe_failures} probe failure(s).",
            recommendation="Check application logs and probe path/port; tune initial delay and timeout only after confirming the application startup and response behavior.",
            score=min(90, 35 + snapshot.probe_failures * 8),
        ))

    findings.sort(key=lambda item: (item.score, item.code), reverse=True)
    risk_score = min(100, max((item.score for item in findings), default=0) + min(15, max(0, len(findings) - 1) * 5))
    if any(item.severity == "critical" for item in findings) or risk_score >= 85:
        status = "critical"
    elif findings:
        status = "degraded"
    else:
        status = "healthy"

    if not findings:
        summary = "No configured risk conditions were detected in this workload snapshot."
        checks = ["Confirm the snapshot is recent and covers all relevant containers.", "Compare against service-level objectives and historical baselines."]
    else:
        summary = f"Detected {len(findings)} finding(s); the highest-priority signal is {findings[0].title.lower()}."
        checks = [finding.recommendation for finding in findings[:3]]

    return IncidentReport(
        cluster=snapshot.cluster,
        namespace=snapshot.namespace,
        workload=snapshot.workload,
        status=status,
        risk_score=risk_score,
        summary=summary,
        findings=findings,
        recommended_checks=checks,
    )
