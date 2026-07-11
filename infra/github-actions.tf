# GitHub Actions OIDC deploy identity.
#
# Lets the deploy workflow (.github/workflows/deploy.yml), when it runs on `main`, assume a
# least-privilege role to sync ui/out to the demo bucket and invalidate CloudFront, with no
# stored AWS keys. Apply this (cd infra && terraform apply), then set the repo Actions variable
# AWS_DEPLOY_ROLE_ARN to the github_actions_deploy_role_arn output (and AWS_S3_BUCKET /
# CLOUDFRONT_DISTRIBUTION_ID to the bucket / distribution_id outputs).
#
# Note: if this AWS account already has a GitHub OIDC provider, import it instead of creating a
# second one (terraform import aws_iam_openid_connect_provider.github <arn>), or swap the resource
# for a data source.

data "tls_certificate" "github" {
  url = "https://token.actions.githubusercontent.com/.well-known/openid-configuration"
}

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.github.certificates[0].sha1_fingerprint]
}

# Trust: only this repo's workflows running on the main branch may assume the role.
data "aws_iam_policy_document" "gha_assume" {
  statement {
    effect  = "Allow"
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
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:ricardogr07/ecg-purkinje-npe:ref:refs/heads/main"]
    }
  }
}

resource "aws_iam_role" "gha_deploy" {
  name               = "${local.project}-gha-deploy"
  assume_role_policy = data.aws_iam_policy_document.gha_assume.json
}

# Permissions: write objects to the demo bucket and invalidate the one distribution. Nothing else.
data "aws_iam_policy_document" "gha_deploy" {
  statement {
    sid       = "ListBucket"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.site.arn]
  }
  statement {
    sid       = "WriteObjects"
    actions   = ["s3:PutObject", "s3:DeleteObject"]
    resources = ["${aws_s3_bucket.site.arn}/*"]
  }
  statement {
    sid       = "InvalidateCache"
    actions   = ["cloudfront:CreateInvalidation"]
    resources = [aws_cloudfront_distribution.site.arn]
  }
}

resource "aws_iam_role_policy" "gha_deploy" {
  name   = "${local.project}-gha-deploy"
  role   = aws_iam_role.gha_deploy.id
  policy = data.aws_iam_policy_document.gha_deploy.json
}

output "github_actions_deploy_role_arn" {
  value = aws_iam_role.gha_deploy.arn
}
