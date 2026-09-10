variable "domain_name" {
  description = "Fully-qualified domain name the certificate covers"
  type        = string
}

variable "zone_id" {
  description = "Route53 hosted zone ID to create the DNS validation record in"
  type        = string
}
