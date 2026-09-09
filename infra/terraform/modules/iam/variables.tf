variable "name" {
  type = string
}

variable "s3_archive_bucket_arn" {
  type = string
}

variable "rds_secret_arn" {
  description = "ARN of the RDS-managed Secrets Manager secret (from module.rds.secret_arn)"
  type        = string
}
