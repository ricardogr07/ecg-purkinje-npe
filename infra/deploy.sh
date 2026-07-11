#!/usr/bin/env bash
# Build the Next.js static export and publish it to S3 + CloudFront.
# Requires: terraform apply already run in infra/ (creates the bucket + distribution).
#
#   ./infra/deploy.sh
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/.." && pwd)"

bucket="$(cd "$here" && terraform output -raw bucket)"
dist="$(cd "$here" && terraform output -raw distribution_id)"
url="$(cd "$here" && terraform output -raw url)"

echo "[deploy] building static export..."
(cd "$root/ui" && npm run build)

echo "[deploy] syncing ui/out -> s3://$bucket"
aws s3 sync "$root/ui/out" "s3://$bucket" --delete

echo "[deploy] invalidating CloudFront $dist"
aws cloudfront create-invalidation --distribution-id "$dist" --paths '/*' >/dev/null

echo "[deploy] done: $url"
