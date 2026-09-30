variable "name" {
  type = string
}

variable "github_repo" {
  description = "GitHub repo allowed to assume this role, as \"owner/repo\" (used for tagging/docs only — the trust policy matches on the immutable IDs below, not this name)"
  type        = string
}

# GitHub's OIDC "sub" claim is "repo:{owner}@{owner_id}/{repo}@{repo_id}:ref:...",
# not the plain "repo:{owner}/{repo}:ref:..." most docs/examples show — so the
# trust policy below matches on the repository_id/repository_owner_id claims
# directly instead of parsing sub. These numeric IDs are immutable for the
# life of the repo/account (stable across renames or transfers), unlike the
# name. Find them by decoding a token's claims (e.g. the debug-oidc job in
# deploy.yml) or via `gh api repos/OWNER/REPO --jq .id,.owner.id`.
variable "github_repository_id" {
  description = "Numeric, immutable GitHub repository id (token's repository_id claim)"
  type        = string
}

variable "github_repository_owner_id" {
  description = "Numeric, immutable GitHub owner/org id (token's repository_owner_id claim)"
  type        = string
}

variable "allowed_ref" {
  description = "Git ref allowed to assume this role (deploys should only run from this branch)"
  type        = string
  default     = "refs/heads/main"
}

variable "deploy_workflow_path" {
  description = "Path (from repo root) of the workflow allowed to assume this role"
  type        = string
  default     = ".github/workflows/deploy.yml"
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

variable "ecs_cluster_arn" {
  description = "Cluster the migration RunTask is scoped to run in (via the ecs:cluster condition)"
  type        = string
}

variable "ecs_task_definition_family_arn" {
  description = "Revision-less task-definition ARN (\"...:family:*\") the migration RunTask is allowed to launch"
  type        = string
}

variable "ecs_execution_role_arn" {
  description = "Task execution role RunTask must be allowed to pass (same one the service's task definition already uses)"
  type        = string
}

variable "ecs_task_role_arn" {
  description = "Task role RunTask must be allowed to pass (same one the service's task definition already uses)"
  type        = string
}
