variable "name" {
  description = "Repository name for the backend API image"
  type        = string
}

variable "untagged_expire_days" {
  type    = number
  default = 14
}
