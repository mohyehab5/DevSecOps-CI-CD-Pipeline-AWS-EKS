# How to Put This Project on Your CV

## 1. Project Title (use this exact line under "Projects")

**DevSecOps CI/CD Pipeline for Containerized Microservices on AWS EKS** — [GitHub link]

## 2. CV Bullet Points (pick 3–5, don't use all of them — keep it tight)

- Designed and built an end-to-end DevSecOps pipeline (GitHub Actions) enforcing 6 automated security gates — SAST, SCA, secret scanning, IaC scanning, container image scanning, and DAST — before any deployment reaches production.
- Provisioned a private, multi-AZ EKS cluster and supporting AWS infrastructure (VPC, ECR, IAM/IRSA) entirely with Terraform, including remote state locking and automated Checkov policy scanning in CI.
- Implemented GitOps continuous deployment with ArgoCD, eliminating direct cluster credentials from the CI pipeline and enabling automatic drift correction and git-based rollback.
- Hardened Kubernetes workloads with Pod Security Admission, NetworkPolicy zero-trust networking, and IRSA, removing root access, standing cloud credentials, and lateral network movement from the runtime environment.
- Eliminated all long-lived cloud credentials from CI/CD using GitHub OIDC federation and AWS IAM role assumption, scoped to a single repository and single AWS resource set.
- Integrated container image signing (Cosign/Sigstore) and immutable ECR tags to provide a verifiable software supply chain from commit to running pod.
- Configured Prometheus/Grafana observability with SLO-based alerting (error rate, latency, crash-loop detection) and documented a git-based incident rollback procedure.

## 3. LinkedIn "Featured" / About Section (short version)

> Built a production-style DevSecOps pipeline on AWS: every commit is automatically tested, statically analyzed, scanned for vulnerable dependencies and leaked secrets, built into a signed container image, and deployed to a hardened, private EKS cluster via GitOps — with zero long-lived cloud credentials anywhere in the pipeline. Full write-up and code: [GitHub link]

## 4. If Asked in an Interview: "Walk me through this project"

Use this structure (matches the `docs/` folder order exactly, so you can literally open the repo and follow along):

1. **The problem**: most CI/CD pipelines deploy fast but don't prove anything is safe. This one gates every stage.
2. **The path**: code push → parallel security scans (SAST/SCA/secrets/IaC) → hardened image build + scan + sign → GitOps deploy via ArgoCD → DAST against the live app → monitored in Prometheus/Grafana.
3. **The one design decision you should be ready to defend**: *why GitOps instead of `kubectl apply` from CI* — because the CI pipeline never needs cluster-admin credentials, and git becomes the full audit trail (see `docs/07-gitops-with-argocd.md`).
4. **The one security decision you should be ready to defend**: *why zero standing AWS credentials* — GitHub OIDC federation + IRSA means a leaked GitHub secret or a compromised pod still can't do anything outside its narrowly scoped role (see `terraform/iam-cicd.tf` and `docs/06-kubernetes-hardening.md`).

## 5. Skills Keyword List (for CV "Skills" section / ATS matching)

`AWS EKS` · `Kubernetes` · `Terraform` · `Docker` · `GitHub Actions` · `CI/CD` · `GitOps` · `ArgoCD` · `DevSecOps` · `SAST` · `SCA` · `DAST` · `Trivy` · `Semgrep` · `OWASP ZAP` · `Gitleaks` · `Checkov` · `OPA/Conftest` · `Cosign/Sigstore` · `IAM` · `IRSA` · `OIDC Federation` · `AWS Secrets Manager` · `Prometheus` · `Grafana` · `NetworkPolicy` · `Pod Security Admission` · `AWS WAF`

---

## ملاحظة بالعربي — إزاي تستخدم الملف ده

- الـ bullet points فوق جاهزة تتلزق في الـ CV زي ما هي (خليها بالإنجليزي حتى لو الـ CV بتاعك عربي، لأن دي المصطلحات اللي الشركات بتدور عليها في الـ ATS).
- متحطش كل الـ bullets — اختار 3 لـ 5 حسب الوظيفة اللي بتقدم عليها: لو DevOps ركز على Terraform/ArgoCD/CI-CD، لو Security ركز على SAST/DAST/IAM/OIDC.
- في الـ interview، متقولش "عملت كل حاجة" — قول القصة بالترتيب اللي في `docs/`، وكن جاهز تشرح بالظبط ليه اخترت GitOps بدل kubectl apply مباشر، وليه شلت كل الـ credentials الثابتة.
- الـ repo ده مصمم إنه "يتفتح ويتشرح لوحده" — يعني لو حد فتح `docs/01` لحد `09` بالترتيب هيفهم القصة كاملة من غيرك، وده بالظبط اللي بيخلي الـ reviewer يصدق إن المشروع حقيقي مش نسخ ولزق.
