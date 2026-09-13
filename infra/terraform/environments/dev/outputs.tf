# api_url uses the raw ALB domain — the frontend and browser-facing API
# calls go through the custom domain (same-origin via CloudFront's /api/*
# behavior); the ALB itself stays HTTP-only behind CloudFront.

output "frontend_url" {
  value = "https://${var.domain_name}"
}

output "cloudfront_domain_name" {
  value = module.frontend_hosting.cloudfront_domain_name
}

output "api_url" {
  value = "http://${module.ecs.alb_dns_name}"
}

output "rds_endpoint" {
  value = module.rds.endpoint
}

output "rds_secret_arn" {
  description = "Secrets Manager ARN holding the RDS master credentials (JSON: username/password)"
  value       = module.rds.secret_arn
}

output "ecr_repository_url" {
  value = module.ecr.repository_url
}

output "s3_archive_bucket" {
  value = module.s3_archive.bucket_name
}

output "github_deploy_role_arn" {
  description = "Role ARN for the GitHub Actions deploy workflow to assume via OIDC"
  value       = module.github_oidc.role_arn
}

output "ecs_cluster_name" {
  value = module.ecs.cluster_name
}

output "ecs_service_name" {
  value = module.ecs.service_name
}

output "frontend_bucket" {
  value = module.frontend_hosting.bucket_name
}

output "cloudfront_distribution_id" {
  value = module.frontend_hosting.distribution_id
}
