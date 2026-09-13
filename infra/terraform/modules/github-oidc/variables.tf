variable "name" {
  type = string
}

variable "github_repo" {
  description = "GitHub repo allowed to assume this role, as \"owner/repo\""
  type        = string
}

variable "allowed_ref" {
  description = "Git ref allowed to assume this role (deploys should only run from this branch)"
  type        = string
  default     = "refs/heads/main"
}

variable "ecr_repository_arn" {
  type = string
}

variable "s3_bucket_arn" {
  type = string
}

variable "cloudfront_distribution_arn" {
  type = string
}

variable "ecs_service_arn" {
  type = string
}
