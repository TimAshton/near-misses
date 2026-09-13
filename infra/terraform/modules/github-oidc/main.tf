# Lets GitHub Actions deploy on push to main without any long-lived AWS
# keys stored as repo secrets: Actions exchanges its workflow OIDC token
# for short-lived credentials under this role, scoped to this repo + branch.

data "tls_certificate" "github" {
  url = "https://token.actions.githubusercontent.com"
}

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.github.certificates[0].sha1_fingerprint]
}

data "aws_iam_policy_document" "assume" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    # Restricts to this repo + branch, matched on the immutable numeric IDs
    # (not name/sub-string matching — see the variable comments) — a workflow
    # run from a fork, a different repo, or a PR branch cannot assume this
    # role, only a push that lands on this repo's main branch.
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:repository_id"
      values   = [var.github_repository_id]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:repository_owner_id"
      values   = [var.github_repository_owner_id]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:ref"
      values   = [var.allowed_ref]
    }

    # AWS requires a GitHub-OIDC trust policy to condition on sub or
    # job_workflow_ref specifically (a bare aud/repository_id/ref set is
    # rejected as "not scoped to all") — job_workflow_ref is the tighter of
    # the two, since it also pins down which workflow file can assume this
    # role, not just which repo/branch.
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:job_workflow_ref"
      values   = ["${var.github_repo}/${var.deploy_workflow_path}@${var.allowed_ref}"]
    }
  }
}

resource "aws_iam_role" "deploy" {
  name               = "${var.name}-github-deploy"
  assume_role_policy = data.aws_iam_policy_document.assume.json
}

data "aws_iam_policy_document" "deploy" {
  # ECR: build+push the backend image. GetAuthorizationToken is account-level
  # only — AWS doesn't support scoping it to a single repository.
  statement {
    sid       = "EcrAuth"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  statement {
    sid = "EcrPush"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
      "ecr:PutImage",
      "ecr:BatchGetImage",
    ]
    resources = [var.ecr_repository_arn]
  }

  # S3: sync the built frontend into the hosting bucket.
  statement {
    sid       = "FrontendBucketWrite"
    actions   = ["s3:PutObject", "s3:DeleteObject"]
    resources = ["${var.s3_bucket_arn}/*"]
  }

  statement {
    sid       = "FrontendBucketList"
    actions   = ["s3:ListBucket"]
    resources = [var.s3_bucket_arn]
  }

  # CloudFront: bust the cache after a frontend deploy.
  statement {
    sid       = "FrontendInvalidate"
    actions   = ["cloudfront:CreateInvalidation", "cloudfront:GetInvalidation"]
    resources = [var.cloudfront_distribution_arn]
  }

  # ECS: roll the API service onto the new :latest image. No
  # RegisterTaskDefinition/PassRole here — the task definition's image tag
  # stays "latest" (mutable ECR tag), so a force-new-deployment is enough to
  # pick up a freshly pushed image without touching the task definition.
  statement {
    sid       = "EcsDeploy"
    actions   = ["ecs:UpdateService", "ecs:DescribeServices"]
    resources = [var.ecs_service_arn]
  }
}

resource "aws_iam_role_policy" "deploy" {
  name   = "${var.name}-github-deploy"
  role   = aws_iam_role.deploy.id
  policy = data.aws_iam_policy_document.deploy.json
}
