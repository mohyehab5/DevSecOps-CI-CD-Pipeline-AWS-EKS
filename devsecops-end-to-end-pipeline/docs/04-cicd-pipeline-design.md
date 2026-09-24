# 04 — CI/CD Pipeline Design

## Objective
Design the GitHub Actions pipeline (`.github/workflows/devsecops-pipeline.yml`) so that every stage is a **hard gate**: a failure at any point stops the pipeline before an insecure artifact can move further downstream.

## Stage Dependency Graph

```
test ──┬──▶ sast ─────┐
       ├──▶ sca ───────┤
       ├──▶ secret-scan┤──▶ build-and-scan-image ──▶ update-manifest-for-gitops ──▶ dast ──▶ notify
       └──▶ iac-scan ──┘
```
`sast`, `sca`, `secret-scan`, and `iac-scan` all run **in parallel** after `test` passes (fast feedback), but `build-and-scan-image` requires **all four** to succeed (`needs: [sast, sca, secret-scan, iac-scan]`) — a vulnerability found by any one scanner blocks the build stage.

## Authentication: Zero Standing Credentials

The pipeline never stores an AWS access key. Instead:
```yaml
permissions:
  id-token: write   # GitHub mints a short-lived OIDC token for this job run only

- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_GITHUB_ACTIONS_ROLE_ARN }}
```
AWS trusts this token because of the OIDC federation configured in `terraform/iam-cicd.tf`, scoped with a `StringLike` condition to **this exact repository and branch** — a workflow running from a fork or a different branch cannot assume the role, even with a valid GitHub Actions token.

## Branch Protection (configured in GitHub repo settings, documented here for completeness)
- `main` requires: this workflow to pass, at least 1 approving review, and up-to-date branch before merge.
- Force-push to `main` disabled; signed commits recommended (not enforced in this template, noted as a next step in `docs/09`).

## Proof of Work
- A pull request that introduces a Semgrep-flagged pattern (e.g. `eval()` on user input) shows a **red X** on the `sast` check and cannot be merged.
- A pull request that adds a dependency with a known CRITICAL CVE fails at `sca` with the specific CVE ID printed in the Trivy output.
- The Actions run summary for a successful `main` push shows all 8 jobs green, ending with a Slack message containing the commit SHA and pipeline status.

## Why It Matters
The pipeline enforces the same rule for every engineer, every time — there's no "just this once, skip the scan" because the scan isn't a separate manual step, it's a required check the branch protection rule depends on.
