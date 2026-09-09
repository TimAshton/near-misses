# frontend_url / api_url use the raw CloudFront/ALB domains since no custom
# domain + ACM cert is wired up yet (would need a Route53 hosted zone
# supplied by the project owner). See PLAN.md.

output "frontend_url" {
  value = "https://${module.frontend_hosting.cloudfront_domain_name}"
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
