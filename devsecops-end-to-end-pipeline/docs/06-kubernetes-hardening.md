# 06 — Kubernetes Hardening

## Objective
Apply defense-in-depth at the cluster level so that even a fully compromised container process has almost nothing it can do: no root, no writable filesystem, no unrestricted network path, no ambient cloud credentials.

## 6.1 Pod Security Admission (Namespace-Level)
`kubernetes/namespace.yaml` labels the namespace `pod-security.kubernetes.io/enforce: restricted` — the strictest built-in profile. Kubernetes itself **rejects at admission time** any pod spec that doesn't meet it (root user, privileged containers, hostPath mounts, etc.), before the scheduler even sees it.

## 6.2 Pod & Container SecurityContext (Defense in Depth)
`kubernetes/deployment.yaml` sets these explicitly even though the namespace already enforces them — so the manifest is safe by default if ever applied to a less-strict namespace:
- `runAsNonRoot: true`, fixed `runAsUser: 1001`
- `readOnlyRootFilesystem: true` (with a small `emptyDir` mounted at `/tmp` for the one place the app needs to write)
- `allowPrivilegeEscalation: false`
- `capabilities: { drop: ["ALL"] }` — no Linux capabilities at all, not even the small ones containers get by default
- `seccompProfile: RuntimeDefault` — blocks a large class of syscalls a compromised process might try

## 6.3 Zero-Trust Networking (`kubernetes/networkpolicy.yaml`)
A `default-deny-all` NetworkPolicy applies to every pod in the namespace first. A second, narrower policy then explicitly allows only: inbound on port 8080 from the load balancer's target-group path, and outbound only to DNS (53) and HTTPS (443). Lateral movement — one compromised pod trying to reach another service it has no business talking to — is blocked at the network layer, not just relying on application-level auth.

## 6.4 No Ambient Cloud Credentials — IRSA
The pod's ServiceAccount (`kubernetes/serviceaccount-and-secrets.yaml`) is annotated with `eks.amazonaws.com/role-arn`, so the pod assumes a narrowly-scoped IAM role directly via the EKS OIDC provider (`terraform/eks.tf`). The underlying EC2 worker node's IAM role is intentionally minimal (`AmazonEKSWorkerNodePolicy`, CNI, ECR read-only) — a pod cannot escalate by reading the node's instance metadata credentials, because IRSA credentials take precedence and are scoped per-pod, not per-node.

## 6.5 Secrets Never in Git
`ExternalSecret` (via the External Secrets Operator) pulls the actual secret value from AWS Secrets Manager at runtime and materializes it as a native `Secret` object inside the cluster. Git only ever contains the **reference** (`prod/db/credentials`), never the value.

## Proof of Work
```bash
# Confirm restricted PSA actually blocks a bad pod spec:
kubectl run test --image=nginx --overrides='{"spec":{"containers":[{"name":"test","image":"nginx","securityContext":{"runAsUser":0}}]}}' -n devsecops-app
# Error from server (Forbidden): pods "test" is forbidden: violates PodSecurity "restricted:latest": runAsNonRoot != true

# Confirm NetworkPolicy blocks lateral movement:
kubectl run attacker --image=busybox -n devsecops-app -- sleep 3600
kubectl exec -n devsecops-app attacker -- wget -T 3 http://devsecops-app.devsecops-app.svc.cluster.local
# times out — attacker pod has no matching NetworkPolicy allowing it to reach the app
```

## Why It Matters
This is the difference between "we run our app in Kubernetes" and "a single compromised pod cannot read node credentials, cannot reach other services, cannot write to its own filesystem, and cannot run as root" — the actual bar a platform security review holds a cluster to.
