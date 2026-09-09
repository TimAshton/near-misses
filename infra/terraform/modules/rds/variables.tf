variable "name" {
  description = "Name prefix for RDS resources"
  type        = string
}

variable "subnet_ids" {
  description = "Private subnet IDs for the DB subnet group"
  type        = list(string)
}

variable "vpc_security_group_ids" {
  description = "Security groups allowed to reach the DB"
  type        = list(string)
}

variable "instance_class" {
  description = "RDS instance class. Kept small deliberately — Phase 1 aviation incident volume is modest (hundreds-low thousands/year); see PLAN.md Open Question #5."
  type        = string
  default     = "db.t4g.micro"
}

variable "allocated_storage" {
  type    = number
  default = 20
}

variable "engine_version" {
  type    = string
  default = "16"
}

variable "db_name" {
  type    = string
  default = "near_misses"
}

variable "username" {
  description = "Master username. Password is NOT set here — AWS manages it in Secrets Manager (manage_master_user_password)."
  type        = string
  default     = "near_misses_app"
}

variable "multi_az" {
  description = "Multi-AZ costs roughly 2x. Off by default for dev; flip on for a production environment."
  type        = bool
  default     = false
}

variable "deletion_protection" {
  type    = bool
  default = false
}

variable "skip_final_snapshot" {
  type    = bool
  default = true
}
