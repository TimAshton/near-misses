variable "name" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "alb_sg_id" {
  type = string
}

variable "ecs_sg_id" {
  type = string
}

variable "ecr_repository_url" {
  type = string
}

variable "image_tag" {
  description = "Image tag to deploy. Defaults to 'latest'; CI should push a real tag and update this via -var or a deploy step once a pipeline exists."
  type        = string
  default     = "latest"
}

variable "container_port" {
  type    = number
  default = 8000
}

variable "cpu" {
  type    = number
  default = 256
}

variable "memory" {
  type    = number
  default = 512
}

variable "desired_count" {
  type    = number
  default = 1
}

variable "execution_role_arn" {
  type = string
}

variable "task_role_arn" {
  type = string
}

variable "environment" {
  description = "Plain (non-secret) env vars for the container"
  type        = map(string)
  default     = {}
}

variable "secrets" {
  description = "Env var name -> Secrets Manager ARN (or ARN:jsonkey) to inject at container start"
  type        = map(string)
  default     = {}
}

variable "log_retention_days" {
  type    = number
  default = 30
}
