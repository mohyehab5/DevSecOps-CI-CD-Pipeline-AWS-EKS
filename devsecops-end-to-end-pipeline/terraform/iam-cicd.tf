# --- GitHub Actions OIDC federation: the pipeline authenticates to AWS with a short-lived
# --- token, never a stored AWS access key/secret in GitHub Secrets. ---

resource "aws_iam_openid_connect_provider" "github_actions" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

resource "aws_iam_role" "github_actions_deploy" {
  name = "github-actions-devsecops-deploy"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Federated = aws_iam_openid_connect_provider.github_actions.arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }
        # Locked to this exact repo + branch — no other repo can assume this role
        StringLike = {
          "token.actions.githubusercontent.com:sub" = "repo:YOUR_GH_ORG/devsecops-end-to-end-pipeline:ref:refs/heads/main"
        }
      }
    }]
  })
}

# Scoped policy: push to this ECR repo + deploy to this EKS cluster ONLY —
# no wildcard "*" resource, no broader account access.
resource "aws_iam_role_policy" "github_actions_deploy_policy" {
  name = "github-actions-deploy-scoped-policy"
  role = aws_iam_role.github_actions_deploy.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*" # required by AWS to be account-wide for this specific action only
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:BatchGetImage"
        ]
        Resource = aws_ecr_repository.app.arn
      },
      {
        Effect   = "Allow"
        Action   = ["eks:DescribeCluster"]
        Resource = aws_eks_cluster.main.arn
      }
    ]
  })
}
