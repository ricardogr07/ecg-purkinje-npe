# Deploy infra for the ecg-purkinje-npe demo: private S3 bucket + CloudFront (HTTPS, OAC).
# Built from scratch for this project. The Next.js static
# export (ui/out) is synced to the bucket; CloudFront serves it over its default *.cloudfront.net
# certificate. Single-page site (one route "/"), so default_root_object=index.html is enough.
#
#   cd infra && terraform init && terraform apply
#   ../infra/deploy.sh    # build + sync + invalidate

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws    = { source = "hashicorp/aws", version = "~> 5.0" }
    random = { source = "hashicorp/random", version = "~> 3.0" }
    tls    = { source = "hashicorp/tls", version = "~> 4.0" }
  }
}

provider "aws" {
  region = "us-east-1" # CloudFront ACM certs must live here; default cert is used anyway
}

resource "random_id" "suffix" {
  byte_length = 3
}

locals {
  project = "ecg-purkinje-npe"
  bucket  = "${local.project}-demo-${random_id.suffix.hex}" # globally-unique
}

# --- private origin bucket (no public access; only CloudFront reads it) ---
resource "aws_s3_bucket" "site" {
  bucket = local.bucket
}

resource "aws_s3_bucket_public_access_block" "site" {
  bucket                  = aws_s3_bucket.site.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- CloudFront Origin Access Control (modern OAI replacement) ---
resource "aws_cloudfront_origin_access_control" "site" {
  name                              = "${local.project}-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

data "aws_cloudfront_cache_policy" "optimized" {
  name = "Managed-CachingOptimized"
}

resource "aws_cloudfront_distribution" "site" {
  enabled             = true
  default_root_object = "index.html"
  comment             = "${local.project} demo"
  price_class         = "PriceClass_100" # NA + EU edges only; cheapest

  origin {
    domain_name              = aws_s3_bucket.site.bucket_regional_domain_name
    origin_id                = "s3-${local.bucket}"
    origin_access_control_id = aws_cloudfront_origin_access_control.site.id
  }

  default_cache_behavior {
    target_origin_id       = "s3-${local.bucket}"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    viewer_protocol_policy  = "redirect-to-https"
    cache_policy_id        = data.aws_cloudfront_cache_policy.optimized.id
    compress               = true
  }

  # Next.js static export ships a 404.html; map missing keys to it.
  custom_error_response {
    error_code         = 403
    response_code      = 404
    response_page_path = "/404.html"
  }
  custom_error_response {
    error_code         = 404
    response_code      = 404
    response_page_path = "/404.html"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true # https://<id>.cloudfront.net
  }
}

# --- bucket policy: allow ONLY this distribution (via OAC) to read ---
data "aws_iam_policy_document" "site" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.site.arn}/*"]
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.site.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "site" {
  bucket = aws_s3_bucket.site.id
  policy = data.aws_iam_policy_document.site.json
}

output "bucket" {
  value = aws_s3_bucket.site.id
}

output "distribution_id" {
  value = aws_cloudfront_distribution.site.id
}

output "url" {
  value = "https://${aws_cloudfront_distribution.site.domain_name}"
}
