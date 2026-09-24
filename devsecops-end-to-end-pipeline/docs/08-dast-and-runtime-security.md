# 08 — DAST & Runtime Security

## Objective
Test the application the way an actual attacker would — by sending real HTTP requests at the **running, deployed** service — since static analysis (SAST) can't catch vulnerabilities that only manifest from runtime behavior, misconfigured headers, or how the app actually responds over the network.

## 8.1 OWASP ZAP Baseline Scan (Pipeline Stage 8)

Runs **after** ArgoCD has synced the new version to the live environment, targeting the real public URL:
```yaml
- name: OWASP ZAP Baseline Scan
  uses: zaproxy/action-baseline@v0.12.0
  with:
    target: "https://app.example.com"
    fail_action: true
```
This performs passive scanning (no destructive payloads) checking for: missing security headers (`Content-Security-Policy`, `X-Frame-Options`, `Strict-Transport-Security`), cookies missing `Secure`/`HttpOnly` flags, verbose error messages leaking stack traces, and outdated/vulnerable JS libraries served by the app.

**`fail_action: true`** means a finding above the configured threshold fails the pipeline job — but by design this runs **after** deployment (DAST needs a live target), so a DAST failure is a signal for immediate rollback (`git revert`, see [07](./07-gitops-with-argocd.md)) rather than a pre-deploy blocker like SAST/SCA.

## 8.2 Edge-Layer Runtime Protection — WAF
See [`security/waf-notes.md`](../security/waf-notes.md) for the full managed rule group list. The WAF sits in front of everything DAST tests, blocking SQLi/XSS/known-bad-input signatures at the ALB before a request ever reaches a pod — this is intentionally a **second, independent layer**, not a substitute for fixing the underlying code issue ZAP might find.

## 8.3 Runtime Anomaly Signal — Prometheus Alerts
`monitoring/prometheus/alert-rules.yaml`'s `HighErrorRate` and `HighP99Latency` alerts double as a lightweight runtime intrusion/abuse signal: a sudden spike in 5xx responses or latency after a deploy is often the first visible sign of either a bug or an active exploitation attempt, and pages the on-call rotation the same way a functional outage would.

## Proof of Work
```bash
curl -I https://app.example.com
# HTTP/2 200
# strict-transport-security: max-age=63072000; includeSubDomains
# x-content-type-options: nosniff
# (headers confirmed present because a prior ZAP finding on missing headers was fixed
#  and re-verified — the actual "prove it" step for a DAST finding: find it, fix it, re-scan clean)
```
```bash
# Confirm WAF is actively blocking, not just logging:
curl "https://app.example.com/?id=1' OR '1'='1"
# HTTP/2 403 — blocked by AWSManagedRulesSQLiRuleSet before reaching the app
```

## Why It Matters
SAST tells you the code *looks* safe. DAST plus a WAF tells you the *running system*, over the actual network, with real HTTP semantics, TLS config, and headers, actually behaves safely — that gap is exactly where a lot of real-world vulnerabilities live.
