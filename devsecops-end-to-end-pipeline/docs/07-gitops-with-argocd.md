# 07 — GitOps with ArgoCD

## Objective
Make git the single, provable source of truth for what's actually running in the cluster — the CI pipeline never has direct `kubectl` access to production; it only ever changes a file in git, and a separate in-cluster controller (ArgoCD) is responsible for making the cluster match.

## Why GitOps Instead of `kubectl apply` in CI
| `kubectl apply` from CI | GitOps (ArgoCD) |
|---|---|
| CI pipeline needs cluster-admin-ish credentials | CI never touches the cluster API at all |
| No automatic drift correction if someone manually `kubectl edit`s something | `selfHeal: true` reverts manual drift back to git automatically |
| "What's running in prod?" = "whatever the last successful pipeline run applied" (not always knowable) | "What's running in prod?" = `git show HEAD:kubernetes/deployment.yaml`, always exactly knowable |
| Rollback = re-run an old pipeline | Rollback = `git revert`, ArgoCD re-syncs automatically |

## How It Works Here

1. CI stage 7 (`update-manifest-for-gitops` in the pipeline) does a simple `sed` to bump the image tag in `kubernetes/deployment.yaml`, then commits and pushes that one-line change back to `main`.
2. `argocd/application.yaml` defines an ArgoCD `Application` watching `kubernetes/` in this repo, with:
   - `automated.prune: true` — resources removed from git are removed from the cluster too
   - `automated.selfHeal: true` — any manual, out-of-band change to a live resource is automatically reverted back to match git within minutes
3. ArgoCD's built-in controller diffs the live cluster state against git every ~3 minutes (and instantly on webhook), and applies only the delta.

## Proof of Work

```bash
argocd app get devsecops-app
# shows Sync Status: Synced, Health Status: Healthy

# Prove self-heal: manually scale the deployment out-of-band
kubectl scale deployment devsecops-app -n devsecops-app --replicas=10

# within ~3 minutes, ArgoCD reverts it back to the replica count Kubernetes' HPA/git defines
kubectl get deployment devsecops-app -n devsecops-app
# replicas back to the git-defined baseline — confirming selfHeal actually fired
```

```bash
# Prove rollback is a pure git operation:
git revert <bad-deploy-commit-sha>
git push
# ArgoCD detects the new commit and rolls the cluster back automatically — no manual
# kubectl rollback, no re-running a pipeline against an old artifact
```

## Why It Matters
Every production change — a new image, a scaled-up replica count, a changed resource limit — has a corresponding git commit, author, and timestamp. That's an audit trail a compliance review or an incident postmortem can actually use, which "someone ran a command from their laptop" never provides.
