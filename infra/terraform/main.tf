terraform {
  required_version = ">= 1.9"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }

  # BOOTSTRAP NOTE: The novakidlife-tfstate bucket and novakidlife-tflock
  # DynamoDB table must exist before running `terraform init`.
  # One-time setup:
  #   aws s3api create-bucket --bucket novakidlife-tfstate --region us-east-1
  #   aws s3api put-bucket-versioning \
  #     --bucket novakidlife-tfstate \
  #     --versioning-configuration Status=Enabled
  #   aws dynamodb create-table \
  #     --table-name novakidlife-tflock \
  #     --attribute-definitions AttributeName=LockID,AttributeType=S \
  #     --key-schema AttributeName=LockID,KeyType=HASH \
  #     --billing-mode PAY_PER_REQUEST \
  #     --region us-east-1
  backend "s3" {
    bucket         = "novakidlife-tfstate"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "novakidlife-tflock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Alias provider for us-east-1 — CloudFront ACM certs must be in us-east-1
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"

  default_tags {
    tags = {
      Project     = var.project
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# ── Local computed values ─────────────────────────────────────────────────────

locals {
  name_prefix  = "${var.project}-${var.environment}"
  service_path = "${path.module}/../../services"
  builds_path  = "${path.module}/builds"
}
