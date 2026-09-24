# End-to-End DevSecOps CI/CD Pipeline on AWS EKS

**A fully automated, security-gated software delivery pipeline — from a git commit to a running, monitored, GitOps-managed workload on Kubernetes — with security enforced at every stage, not bolted on at the end.**

![DevSecOps](https://img.shields.io/badge/DevSecOps-Shift--Left-blueviolet) ![AWS](https://img.shields.io/badge/AWS-EKS-orange) ![GitOps](https://img.shields.io/badge/GitOps-ArgoCD-informational) ![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

---

## 1. Project Summary

This repository is a complete, working DevSecOps pipeline built around one principle: **security is a pipeline stage, not a final review**. A code change only reaches production after passing through code quality checks, static analysis (SAST), dependency scanning (SCA), secret scanning, infrastructure-as-code scanning, a hardened container build, image signing, and dynamic testing against the live environment (DAST) — all automated, all blocking on failure.

It intentionally reuses the same AWS networking discipline from the [`aws-enterprise-multitier-infrastructure`](../aws-enterprise-multitier-infrastructure) project (private subnets, least-privilege IAM, no direct internet exposure for workloads) and extends it into a full container/Kubernetes delivery platform.

## 2. Pipeline Flow

```
 Developer push
       │
       ▼
 ┌─────────────┐   ┌───────────┐   ┌───────────┐   ┌──────────────┐
 │ Lint + Unit │──▶│   SAST    │   │    SCA    │   │ Secret Scan  │
 │    Tests    │   │ (Semgrep) │   │  (Trivy)  │   │  (Gitleaks)  │
 └─────────────┘   └───────────┘   └───────────┘   └──────────────┘
                              │  all must pass  │
                              ▼
                    ┌───────────────────┐
                    │   IaC Scanning     │  Checkov (Terraform) + OPA/Conftest (K8s manifests)
                    └───────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ Build container image (hardened,│
              │ non-root, multi-stage)          │
              │ → Trivy image scan (blocks on   │
              │   CRITICAL CVEs)                │
              │ → Push to ECR (immutable tags)  │
              │ → Sign with Cosign (Sigstore)   │
              └───────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ Update image tag in git         │  ← GitOps: pipeline never
              │ (kubernetes/deployment.yaml)    │    runs kubectl apply directly
              └───────────────────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │  ArgoCD auto-syncs │  cluster state = git state, always
                    │  the EKS cluster    │
                    └───────────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │  DAST (OWASP ZAP)  │  tests the *running* app for real vulnerabilities
                    └───────────────────┘
                              │
                              ▼
                    Slack notification + Prometheus/Grafana monitoring live
```

## 3. Repository Structure

```
devsecops-end-to-end-pipeline/
├── README.md
├── CV_GUIDE.md                          → how to describe this project on a CV/LinkedIn
├── app/                                  → sample Flask microservice
│   ├── src/app.py
│   ├── tests/test_app.py
│   ├── requirements.txt
│   └── Dockerfile                        → hardened, multi-stage, non-root
├── terraform/                            → IaC: VPC, EKS, ECR, IAM/IRSA/OIDC
│   ├── main.tf, vpc.tf, eks.tf, ecr.tf, iam-cicd.tf, variables.tf, outputs.tf
├── kubernetes/                           → K8s manifests (GitOps source of truth)
│   ├── namespace.yaml, deployment.yaml, service.yaml, ingress.yaml
│   ├── hpa.yaml, networkpolicy.yaml, serviceaccount-and-secrets.yaml
├── .github/workflows/
│   └── devsecops-pipeline.yml            → the full 8-stage CI/CD pipeline
├── argocd/
│   └── application.yaml                  → GitOps continuous deployment definition
├── security/
│   ├── opa-policies/deployment-security.rego
│   ├── gitleaks.toml, .checkov.yaml, .trivyignore
│   └── waf-notes.md
├── monitoring/
│   └── prometheus/scrape-config.yaml, alert-rules.yaml
├── docs/
│   ├── 01-architecture-overview.md
│   ├── 02-infrastructure-as-code.md
│   ├── 03-containerization-and-image-security.md
│   ├── 04-cicd-pipeline-design.md
│   ├── 05-shift-left-security-sast-sca-secrets.md
│   ├── 06-kubernetes-hardening.md
│   ├── 07-gitops-with-argocd.md
│   ├── 08-dast-and-runtime-security.md
│   └── 09-observability-and-incident-response.md
└── LICENSE
```

## 4. Security Controls Implemented (Shift-Left Map)

| Stage | Control | Tool |
|---|---|---|
| Code | Static Application Security Testing | Semgrep (OWASP Top 10 ruleset) |
| Code | Dependency vulnerability scanning | Trivy (filesystem mode) |
| Code | Secret detection (full git history) | Gitleaks |
| Infra | IaC misconfiguration scanning | Checkov |
| Infra | Kubernetes manifest policy enforcement | OPA / Conftest |
| Build | Container image vulnerability scanning | Trivy (image mode, scan-on-push in ECR too) |
| Build | Supply-chain image signing | Cosign (keyless, OIDC-based) |
| Build | Immutable image tags | ECR `IMAGE_TAG_MUTABILITY=IMMUTABLE` |
| Deploy | No long-lived cloud credentials | GitHub OIDC → AWS IAM role assumption |
| Deploy | Least-privilege pipeline IAM | Scoped to one ECR repo + one EKS cluster only |
| Runtime | Non-root, read-only rootfs, no priv-esc | Pod SecurityContext + Pod Security Admission |
| Runtime | Zero-trust pod networking | Kubernetes NetworkPolicy (default-deny) |
| Runtime | Secrets never in git | External Secrets Operator ↔ AWS Secrets Manager |
| Runtime | Edge/WAF protection | AWS WAFv2 managed rule groups on the ALB |
| Runtime | Dynamic vulnerability testing | OWASP ZAP baseline scan against the live app |
| Operate | Metrics, alerting, audit trail | Prometheus + Grafana + EKS control-plane audit logs |

## 5. Why This Project Exists

Most "DevOps" portfolio projects stop at "I built a CI/CD pipeline that deploys to Kubernetes." This one answers the follow-up questions a real interview asks: *How do you know the code is safe before it ships? How do you know the image doesn't have known CVEs? How do you stop someone from committing a secret? How do you know the cluster matches what's in git? How do you find out if something goes wrong at 3am?* — every one of those has a concrete, working answer in this repo.

## 6. How to Read This Repository

Start with [`docs/01-architecture-overview.md`](./docs/01-architecture-overview.md), then follow the docs in order — they mirror the pipeline flow above. Each doc explains the **objective**, what was **built**, and **why** the specific tool/design choice was made over the alternatives.

For how to present this project on a CV, see [`CV_GUIDE.md`](./CV_GUIDE.md).
