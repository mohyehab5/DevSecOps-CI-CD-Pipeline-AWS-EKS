resource "aws_ecr_repository" "app" {
  name                 = "devsecops-demo-app"
  image_tag_mutability = "IMMUTABLE" # prevents tag-overwrite supply-chain attacks

  image_scanning_configuration {
    scan_on_push = true # every pushed image is scanned automatically
  }

  encryption_configuration {
    encryption_type = "KMS"
  }
}

resource "aws_ecr_lifecycle_policy" "app" {
  repository = aws_ecr_repository.app.name

  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep only the last 15 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 15
      }
      action = { type = "expire" }
    }]
  })
}

resource "aws_ecr_registry_scanning_configuration" "main" {
  scan_type = "ENHANCED" # continuous rescanning against the CVE database, not just at push time

  rule {
    scan_frequency = "CONTINUOUS_SCAN"
    repository_filter {
      filter      = "*"
      filter_type = "WILDCARD"
    }
  }
}
