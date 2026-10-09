# KubeSage — Kubernetes Incident Intelligence

KubeSage is a small, extensible AIOps service that turns operational signals into explainable incident assessments. It combines deterministic rules, impact scoring, and actionable remediation guidance behind a FastAPI API.

The first version intentionally keeps the analysis engine transparent: every finding includes the signal that triggered it, a severity, and a practical next step. This makes it useful for demos, local testing, and as a foundation for connecting real cluster telemetry later.

## What it does

- Accepts Kubernetes-style workload signals through a REST API.
- Detects common conditions such as repeated restarts, unavailable replicas, high CPU/memory usage, and failed probes.
- Produces a prioritized incident summary with evidence and suggested checks.
- Exposes health and readiness endpoints for container and Kubernetes probes.
- Includes Docker, Kubernetes manifests, automated tests, and a CI workflow.

## Architecture

```text
Telemetry / operator input
          |
          v
      FastAPI API
          |
          v
  Rule-based analysis engine
          |
          v
 Incident findings + next steps
```

## Run locally

Requires Python 3.11+.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for the interactive API docs.

## Example request

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "cluster": "dev-cluster",
    "namespace": "payments",
    "workload": "checkout-api",
    "desired_replicas": 4,
    "available_replicas": 2,
    "restart_count": 9,
    "cpu_percent": 91,
    "memory_percent": 72,
    "probe_failures": 3
  }'
```

## Run with Docker

```bash
docker build -t kubesage:local .
docker run --rm -p 8000:8000 kubesage:local
```

Or use Docker Compose:

```bash
docker compose up --build
```

## Kubernetes deployment

The starter manifests are in `deploy/kubernetes/`. Review resource requests, limits, and replica counts before using them in a real environment.

```bash
kubectl apply -f deploy/kubernetes/
kubectl get pods -l app=kubesage
kubectl port-forward service/kubesage 8000:8000
```

The included manifests deploy the API only. They do not yet collect metrics from a live cluster or automatically restart workloads. Remediation advice is informational; it does not execute changes in your cluster.

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Service metadata |
| GET | `/health` | Liveness check |
| GET | `/ready` | Readiness check |
| POST | `/analyze` | Analyze one workload snapshot |

## Development

```bash
pip install -r requirements.txt
pytest -q
```

## Roadmap

- Add Prometheus metrics ingestion and alert correlation.
- Add Kubernetes API discovery with read-only RBAC.
- Persist incident history and support deduplication.
- Add configurable policies and service-level objectives.
- Add optional LLM summaries behind an explicit, opt-in provider interface.

## Security notes

Do not expose the API publicly without authentication and network controls. Use least-privilege service accounts, store secrets outside source control, and validate all telemetry sources before connecting this service to a production cluster.

## License

MIT — see [LICENSE](LICENSE).
