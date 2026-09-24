# 05 — Shift-Left Security: SAST, SCA & Secret Scanning

## Objective
Catch three distinct classes of vulnerability **before a container is ever built**: insecure code patterns (SAST), vulnerable dependencies (SCA), and leaked credentials (secret scanning) — each with a different tool, because no single scanner catches all three well.

## 5.1 SAST — Semgrep

Runs the `p/owasp-top-ten` public ruleset against the application source on every push. Findings are uploaded as SARIF to GitHub's native **Security tab**, so they show up alongside Dependabot alerts in one place rather than a separate dashboard.

**Proof**: a deliberately-introduced pattern like `subprocess.run(user_input, shell=True)` is flagged as a command-injection risk in the PR checks, with the exact file/line annotated inline on the diff.

## 5.2 SCA — Trivy (filesystem mode)

Scans `requirements.txt` against the National Vulnerability Database + multiple vendor advisories. Configured with `exit-code: 1` and `severity: CRITICAL,HIGH` — the build stage literally cannot proceed while a high/critical CVE exists in a direct dependency.

**Proof**: pinning `flask` to a version with a known published CVE causes the `sca` job to fail with the CVE ID, affected package, and fixed version printed directly in the job log.

## 5.3 Secret Scanning — Gitleaks

Runs with `fetch-depth: 0` (full git history, not just the latest commit) — because a secret committed and then "removed" in a later commit is still exposed in git history forever unless the history itself is rewritten. Gitleaks catches this even if the current `HEAD` looks clean.

**Proof**: committing a string matching an AWS access key pattern (`AKIA[0-9A-Z]{16}`) anywhere in the diff, even in a commit later reverted, is caught the moment it's pushed — verified by testing with a clearly-fake, non-functional key pattern in a scratch branch.

## Design Decision: Why Three Separate Tools Instead of One

| Tool | Strength | Weakness if used alone |
|---|---|---|
| Semgrep (SAST) | Understands code logic/data flow | Doesn't know about published CVEs in third-party packages |
| Trivy (SCA) | Matches against CVE databases | Doesn't understand your own code's logic bugs |
| Gitleaks | Purpose-built entropy + pattern matching across history | Not designed to find logic bugs or CVEs at all |

Running all three in parallel, each doing the one thing it's actually good at, catches a materially wider set of issues than any single "all-in-one" scanner — and keeps each job's failure message specific and actionable instead of a generic "security scan failed."

## Why It Matters
"Shift-left" isn't a slogan here — a vulnerability found at the SAST stage costs one failed CI job; the same vulnerability found in production costs an incident, a patch, a redeploy, and possibly a disclosure.
