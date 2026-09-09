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
