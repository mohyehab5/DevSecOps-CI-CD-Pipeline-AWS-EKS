# 01 — Architecture Overview

## Objective
Establish the full system topology: source control → CI/CD → container registry → Kubernetes on EKS → GitOps reconciliation → observability, and show how security tooling sits at each boundary rather than as a separate audit step.

## Components

| Layer | Component | Role |
|---|---|---|
| Source | GitHub | Single source of truth for both application code and cluster desired-state (`kubernetes/`) |
| CI | GitHub Actions | Runs test/SAST/SCA/secret-scan/IaC-scan/build/sign stages |
| Registry | Amazon ECR | Stores immutable, scan-on-push, signed container images |
| Cluster | Amazon EKS | Runs the workload across 2 AZs, private worker nodes, public control-plane endpoint locked to known CIDRs |
| GitOps | ArgoCD | Continuously reconciles the live cluster state to match `kubernetes/` in git |
| Secrets | AWS Secrets Manager + External Secrets Operator | Secrets never stored in git or CI variables |
| Identity | IAM OIDC (GitHub Actions) + IRSA (pods) | Both the pipeline and the running pods use short-lived, scoped credentials — zero static AWS keys anywhere |
| Edge | AWS ALB + WAFv2 | TLS termination, managed rule groups, rate limiting |
| Observability | Prometheus + Grafana + EKS audit logs | Metrics, alerting, and a full audit trail of control-plane actions |

## Design Principles Applied

1. **No standing credentials anywhere.** Both the CI pipeline and the running pods authenticate to AWS via short-lived, federated identity (OIDC/IRSA) — there is no AWS access key stored in GitHub Secrets or baked into any image.
2. **Git is the only place cluster state is defined.** The pipeline never runs `kubectl apply`; it updates a manifest in git, and ArgoCD is the only thing that talks to the cluster's API to apply changes. This gives a full audit trail (`git log`) of every production change.
3. **Every artifact is scanned at least twice.** Dependencies are scanned as source (Trivy fs mode) and the built image is scanned again (Trivy image mode + ECR continuous scanning) — catching anything introduced during the build itself.
4. **Fail closed, not open.** Every security gate (`exit-code: 1` in Trivy, `soft-fail: false` in Checkov, WAF blocking mode) stops the pipeline or blocks the request rather than just logging a warning.

## Why It Matters
This mirrors how a real platform team structures a delivery pipeline: the "path to production" is a single, auditable, automated sequence — not a developer running scripts from their laptop and a security team reviewing after the fact.
