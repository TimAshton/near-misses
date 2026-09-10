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
