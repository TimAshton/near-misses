variable "bucket_name" {
  description = "Globally-unique S3 bucket name for the static frontend build"
  type        = string
}

variable "name" {
  type = string
}

variable "api_origin_domain_name" {
  description = <<-EOT
    ALB DNS name to route /api/* and /ws through this same CloudFront
    distribution. Without a purchased domain there's no ACM cert for the
    ALB, so the frontend (served over HTTPS by CloudFront's default cert)
    can't call it directly — browsers block that as mixed content. Routing
    both through one CloudFront distribution makes them same-origin and
    keeps CloudFront-to-ALB traffic over plain HTTP (server-to-server, not
    subject to browser mixed-content rules).
  EOT
  type        = string
}
