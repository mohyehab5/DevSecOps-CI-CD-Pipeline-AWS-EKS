terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state: never store state locally or in git.
  # State bucket has versioning + encryption enabled (see terraform/state-bootstrap notes in docs/02).
  backend "s3" {
    bucket         = "devsecops-project-tfstate"
    key            = "eks/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "devsecops-end-to-end-pipeline"
      ManagedBy   = "terraform"
      Environment = var.environment
    }
  }
}
