# Remote-state decision: this environment uses LOCAL state for now.
#
# A S3+DynamoDB remote backend is the standard choice, but it has a
# chicken-and-egg problem: the bucket/table have to exist before `terraform
# init` can point at them, and creating them via Terraform itself (in this
# same config) can't happen before the backend is configured. Since no such
# bootstrap bucket exists yet in this account, local state keeps
# `terraform init`/`validate`/`apply` working out of the box.
#
# To migrate to remote state once this environment is stable:
#   1. Create a state bucket + lock table once, out-of-band (or via a small
#      one-off `bootstrap/` Terraform config kept separate from this one):
#        aws s3api create-bucket --bucket near-misses-tfstate-<suffix> --region us-west-2 \
#          --create-bucket-configuration LocationConstraint=us-west-2
#        aws dynamodb create-table --table-name near-misses-tf-locks \
#          --attribute-definitions AttributeName=LockID,AttributeType=S \
#          --key-schema AttributeName=LockID,KeyType=HASH \
#          --billing-mode PAY_PER_REQUEST
#   2. Uncomment the backend block below and fill in the bucket name.
#   3. Run `terraform init -migrate-state`.
#
# terraform {
#   backend "s3" {
#     bucket         = "near-misses-tfstate-<suffix>"
#     key            = "dev/terraform.tfstate"
#     region         = "us-west-2"
#     dynamodb_table = "near-misses-tf-locks"
#     encrypt        = true
#   }
# }
