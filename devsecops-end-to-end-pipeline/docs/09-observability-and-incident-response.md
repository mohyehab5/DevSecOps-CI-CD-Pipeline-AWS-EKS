# 09 — Observability & Incident Response

## Objective
Make sure that when something breaks (a bad deploy, a spike in errors, a security event) it's detected by an alert within minutes, not discovered by a user complaint — and that there's a clear, git-based path to remediate it.

## 9.1 Application Metrics
`app/src/app.py` exposes a native `/metrics` endpoint (Prometheus client library) tracking request count by endpoint/status and request latency as a histogram. `monitoring/prometheus/scrape-config.yaml` defines a `ServiceMonitor` so the Prometheus Operator auto-discovers and scrapes it every 15s — no manual Prometheus config file edits needed per-service.

## 9.2 Alerting Rules (`monitoring/prometheus/alert-rules.yaml`)
| Alert | Trigger | Signals |
|---|---|---|
| `HighErrorRate` | >5% of requests are 5xx for 5 min | Bad deploy, downstream dependency failure |
| `PodCrashLooping` | Any pod restarting repeatedly for 5 min | OOM, bad config, failing readiness probe |
| `HighP99Latency` | P99 latency > 1s for 10 min | Resource exhaustion, DB slowness, possible abuse traffic |

Alerts route to Alertmanager → Slack (same channel as the pipeline's `notify` job), so deploy events and health alerts are visible side-by-side, making "did the last deploy cause this?" a 10-second question to answer, not a 30-minute log dig.

## 9.3 Audit Trail — Three Independent Logs
1. **Git history** — every application code change, every infra change (Terraform), every cluster desired-state change (image tag bumps, manifest edits) — who, when, what, all in `git log`.
2. **EKS control-plane audit logs** (enabled in `terraform/eks.tf`) — every Kubernetes API call against the cluster, including anything done manually outside of ArgoCD.
3. **CloudTrail** (implicit via standard AWS account setup) — every AWS API call the pipeline's IAM role or any engineer made.

Cross-referencing these three is how a real incident review reconstructs "what actually happened" without relying on anyone's memory.

## 9.4 Incident Response Flow (as implemented by this repo's tooling)

```
Alert fires (Slack)
    │
    ▼
On-call checks Grafana dashboard for the affected metric
    │
    ▼
Is this correlated with a recent deploy? (check #pipeline-notifications timestamp)
    │
    ├─ Yes → git revert the offending commit → push → ArgoCD auto-syncs the rollback
    │         (typically < 5 minutes from decision to rolled-back cluster state)
    │
    └─ No  → check EKS audit logs / CloudTrail for out-of-band changes,
              or scale/resource issue → HPA should already be reacting (see kubernetes/hpa.yaml)
```

## Proof of Work
```bash
# Simulate an incident: force an error rate spike
kubectl exec -n devsecops-app deploy/devsecops-app -- sh -c "for i in $(seq 1 200); do curl -s -o /dev/null http://localhost:8080/nonexistent; done"

# HighErrorRate alert fires within 5 minutes in Alertmanager, visible in Grafana's
# error-rate panel, and a Slack notification lands in the alerts channel.
```

## Why It Matters
A pipeline that ships fast but has no idea when it ships something broken isn't actually "production-grade." The combination of app-level metrics, alerting thresholds, and a GitOps rollback path turns "we monitor the app" into a specific, timed, repeatable incident-response procedure.
