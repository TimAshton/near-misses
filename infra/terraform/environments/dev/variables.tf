variable "aws_region" {
  type    = string
  default = "us-west-2"
}

variable "project_name" {
  type    = string
  default = "near-misses"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "azs" {
  description = "Two AZs in aws_region to spread subnets across"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b"]
}

variable "root_domain" {
  description = "Route53 hosted zone name that owns domain_name"
  type        = string
  default     = "tashton.com"
}

variable "domain_name" {
  description = "Custom domain the frontend/API are served on"
  type        = string
  default     = "incidents.tashton.com"
}

variable "github_repo" {
  description = "GitHub repo (owner/name) allowed to assume the CI deploy role via OIDC"
  type        = string
  default     = "TimAshton/near-misses"
}

# Immutable GitHub IDs the OIDC trust policy matches on — see the comment on
# github_repository_id in modules/github-oidc/variables.tf for why. Found via
# `gh api repos/TimAshton/near-misses --jq '.id, .owner.id'`.
variable "github_repository_id" {
  type    = string
  default = "1363014236"
}

variable "github_repository_owner_id" {
  type    = string
  default = "10035299"
}
