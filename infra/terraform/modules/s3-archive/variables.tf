variable "bucket_name" {
  description = "Globally-unique S3 bucket name for raw API response archive"
  type        = string
}

variable "glacier_transition_days" {
  type    = number
  default = 90
}

variable "expiration_days" {
  description = "Adjust or remove if long-term retention of raw responses is desired"
  type        = number
  default     = 365
}
