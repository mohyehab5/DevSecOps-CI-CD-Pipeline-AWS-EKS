# 03 — Containerization & Image Security

## Objective
Build a container image that is small, reproducible, scanned, signed, and cannot run with more privilege than it needs — hardened at every layer of the Dockerfile, not just at deploy time.

## Dockerfile Hardening (`app/Dockerfile`)

| Control | How |
|---|---|
| Minimal attack surface | Multi-stage build — build tools and pip cache never reach the final image |
| No root | Dedicated `appuser` (UID 1001), `USER appuser` before `CMD` |
| Reproducibility | Base image pinned to `python:3.12-slim` (specific tag, never `latest`) |
| Health checks | `HEALTHCHECK` instruction so the orchestrator can detect a hung process, independent of the K8s liveness probe |
| Production server | `gunicorn`, not Flask's development server (`flask run` is explicitly unsafe for production — no WSGI hardening, single-threaded) |

## Build & Scan Pipeline (CI stage 6, `.github/workflows/devsecops-pipeline.yml`)

1. `docker build` — produces the immutable, SHA-tagged image.
2. **Trivy image scan** — `severity: CRITICAL`, `exit-code: 1`: a single unresolved CRITICAL CVE in the OS packages or Python dependencies **blocks the push**.
3. **Push to ECR** — `IMAGE_TAG_MUTABILITY=IMMUTABLE` means this exact tag can never be overwritten later (prevents a class of supply-chain attack where a "known-good" tag is silently swapped).
4. **Cosign signing** — keyless signing using the GitHub Actions OIDC identity as the signing identity (via Sigstore's Fulcio/Rekor), so there's a publicly verifiable, tamper-evident record of *which pipeline run* produced *which exact image digest*.

## Proof of Work

```bash
# Verify the image was actually signed by this pipeline (not hand-pushed by someone with ECR access)
cosign verify \
  --certificate-identity "https://github.com/YOUR_GH_ORG/devsecops-end-to-end-pipeline/.github/workflows/devsecops-pipeline.yml@refs/heads/main" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  <account>.dkr.ecr.us-east-1.amazonaws.com/devsecops-demo-app:<sha>
```
```bash
# Confirm non-root at runtime
kubectl exec -n devsecops-app deploy/devsecops-app -- id
# uid=1001(appuser) gid=1001(appgroup)
```
```bash
# Confirm the image scan gate actually blocks: intentionally add a known-vulnerable
# package version to requirements.txt and push — pipeline fails at the Trivy image-scan step,
# never reaches the push/deploy stages.
```

## Why It Matters
A signed, scanned, non-root, immutable image is what turns "we use Docker" into "we can prove exactly what code is running in production and that nobody tampered with it between build and deploy" — the actual question a security review asks.
