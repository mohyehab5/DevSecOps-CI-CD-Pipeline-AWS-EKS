# 02 — Infrastructure as Code (Terraform)

## Objective
Provision every piece of AWS infrastructure — networking, EKS, ECR, IAM — through Terraform, with remote state, drift protection, and automated scanning of the IaC itself before anything is applied.

## What's Provisioned (`/terraform`)
- **`vpc.tf`** — 2 public + 2 private subnets across 2 AZs, IGW + NAT Gateway, matching the private-worker-node pattern from the base networking project.
- **`eks.tf`** — EKS cluster with control-plane audit logging enabled (`api`, `audit`, `authenticator`, `controllerManager`, `scheduler`), KMS-encrypted Kubernetes Secrets at rest, and an IAM OIDC provider for IRSA. Worker nodes deploy **only** into private subnets.
- **`ecr.tf`** — immutable image tags, scan-on-push, and enhanced continuous re-scanning (catches CVEs disclosed *after* an image was already pushed and marked "clean").
- **`iam-cicd.tf`** — the GitHub Actions OIDC trust relationship, scoped to exactly one repo/branch and exactly two permissions (push to this ECR repo, describe this EKS cluster) — not `AdministratorAccess`.

## Remote State & Locking

```bash
# one-time bootstrap (run manually, before `terraform init` against the backend):
aws s3 mb s3://devsecops-project-tfstate
aws s3api put-bucket-versioning --bucket devsecops-project-tfstate --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket devsecops-project-tfstate --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

aws dynamodb create-table --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```
State is versioned (recoverable if corrupted) and lock-protected (prevents two engineers/pipelines from applying concurrently and corrupting state).

## Standard Workflow

```bash
cd terraform
terraform init
terraform plan -out=tfplan
# checkov + conftest run against this same directory in CI before any apply is allowed
terraform apply tfplan
```

## Proof of Work
- `terraform plan` run in CI on every pull request touching `terraform/`, with the plan output posted as a PR comment for human review before merge.
- `checkov -d terraform/` returns zero HIGH/CRITICAL findings (see [`security/.checkov.yaml`](../security/.checkov.yaml) for the one explicitly-documented exception).
- After `apply`, `terraform output eks_cluster_endpoint` and `aws eks describe-cluster --name devsecops-eks-cluster` return matching, healthy cluster state.

## Why It Matters
Infrastructure changes go through the exact same review/scan/merge discipline as application code — a misconfigured security group or an over-permissioned IAM role gets caught by Checkov in CI, not discovered during a security incident.
