resource "aws_ecr_repository" "notify_environment" {
  name = "notify_environment"
  image_tag_mutability = "MUTABLE"

  encryption_configuration {
    encryption_type = "AES256"
  }

  image_scanning_configuration {
    scan_on_push = "true"
  }
}

locals {
  ecr-lifecycle-policy = {
    rules = [
      {
        action = {
          type = "expire"
        }
        rulePriority = 1
        selection = {
          countNumber = 5
          countType = "imageCountMoreThan"
          tagStatus = "any"
        }
      }
    ]
  }
}

resource "aws_ecr_lifecycle_policy" "notify_environment" {
  repository = aws_ecr_repository.notify_environment.name
  policy = jsonencode(local.ecr-lifecycle-policy)
}