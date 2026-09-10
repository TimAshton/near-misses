terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# CloudFront requires its ACM certificate to live in us-east-1 regardless of
# which region the rest of the stack runs in.
provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

locals {
  name = "${var.project_name}-${var.environment}"
}

data "aws_route53_zone" "root" {
  name         = "${var.root_domain}."
  private_zone = false
}

# S3 bucket names must be globally unique across all of AWS — suffix with a
# random id rather than guessing an available name.
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

module "network" {
  source = "../../modules/network"

  name = local.name
  azs  = var.azs
}

module "ecr" {
  source = "../../modules/ecr"

  name = "${local.name}-api"
}

module "s3_archive" {
  source = "../../modules/s3-archive"

  bucket_name = "${local.name}-archive-${random_id.bucket_suffix.hex}"
}

module "certificate" {
  source = "../../modules/certificate"
  providers = {
    aws.us_east_1 = aws.us_east_1
  }

  domain_name = var.domain_name
  zone_id     = data.aws_route53_zone.root.zone_id
}

module "frontend_hosting" {
  source = "../../modules/frontend-hosting"

  name                   = local.name
  bucket_name            = "${local.name}-frontend-${random_id.bucket_suffix.hex}"
  api_origin_domain_name = module.ecs.alb_dns_name
  aliases                = [var.domain_name]
  acm_certificate_arn    = module.certificate.certificate_arn
}

resource "aws_route53_record" "frontend_a" {
  zone_id = data.aws_route53_zone.root.zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = module.frontend_hosting.cloudfront_domain_name
    zone_id                = module.frontend_hosting.cloudfront_hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "frontend_aaaa" {
  zone_id = data.aws_route53_zone.root.zone_id
  name    = var.domain_name
  type    = "AAAA"

  alias {
    name                   = module.frontend_hosting.cloudfront_domain_name
    zone_id                = module.frontend_hosting.cloudfront_hosted_zone_id
    evaluate_target_health = false
  }
}

module "rds" {
  source = "../../modules/rds"

  name                   = local.name
  subnet_ids             = module.network.private_subnet_ids
  vpc_security_group_ids = [module.network.rds_sg_id]
}

module "iam" {
  source = "../../modules/iam"

  name                  = local.name
  s3_archive_bucket_arn = module.s3_archive.bucket_arn
  rds_secret_arn        = module.rds.secret_arn
}

module "ecs" {
  source = "../../modules/ecs"

  name               = local.name
  vpc_id             = module.network.vpc_id
  public_subnet_ids  = module.network.public_subnet_ids
  private_subnet_ids = module.network.private_subnet_ids
  alb_sg_id          = module.network.alb_sg_id
  ecs_sg_id          = module.network.ecs_sg_id
  ecr_repository_url = module.ecr.repository_url
  execution_role_arn = module.iam.execution_role_arn
  task_role_arn      = module.iam.task_role_arn

  environment = {
    DB_HOST    = module.rds.address
    DB_PORT    = tostring(module.rds.port)
    DB_NAME    = module.rds.db_name
    DB_USER    = module.rds.username
    S3_BUCKET  = module.s3_archive.bucket_name
    AWS_REGION = var.aws_region
  }

  secrets = {
    DB_SECRET_JSON = module.rds.secret_arn
  }
}
