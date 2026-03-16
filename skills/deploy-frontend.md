# Skill: Deploy Frontend

**Purpose:** Build Next.js static export and deploy to S3, then invalidate CloudFront.

## Prerequisites
- AWS CLI configured with deployment credentials
- `CLOUDFRONT_DISTRIBUTION_ID` available (from SSM or .env)
- S3 bucket `novakidlife-web` exists (provisioned by Terraform)

## Steps

### 1. Type-check and build
```bash
cd apps/web
npm run type-check
npm run build
```
Build output lands in `apps/web/out/`. Verify no build errors before proceeding.

### 2. Sync to S3
```bash
aws s3 sync apps/web/out/ s3://novakidlife-web \
  --delete \
  --cache-control "public, max-age=31536000, immutable" \
  --exclude "*.html" \
  --exclude "*.json"

# HTML and JSON files get shorter cache (they change on deploys)
aws s3 sync apps/web/out/ s3://novakidlife-web \
  --delete \
  --cache-control "public, max-age=0, must-revalidate" \
  --include "*.html" \
  --include "*.json"
```

### 3. Invalidate CloudFront
```bash
DIST_ID=$(aws ssm get-parameter \
  --name /novakidlife/aws/cloudfront-distribution-id \
  --query Parameter.Value --output text)

aws cloudfront create-invalidation \
  --distribution-id "$DIST_ID" \
  --paths "/*"
```

### 4. Verify
```bash
curl -I https://novakidlife.com | head -5
```
Expect `HTTP/2 200` and `x-cache: Hit from cloudfront` within ~60 seconds.

## Rollback
Re-deploy the previous git tag:
```bash
git checkout <previous-tag>
npm run build --workspace=apps/web
# repeat sync + invalidation steps
```
