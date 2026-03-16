# Skill: Terraform Apply

**Purpose:** Apply reviewed infrastructure changes. Always run after `terraform-plan.md`.

## Prerequisites
- `tfplan` file exists from a recent `terraform plan -out=tfplan`
- Plan has been reviewed and approved
- No red (`-`) destroy operations unless explicitly intended

## Steps

### 1. Confirm the plan is recent
```bash
# tfplan should be from the current session
ls -la infra/terraform/tfplan
```
If tfplan is older than 30 minutes, re-run `terraform plan -out=tfplan`.

### 2. Apply the saved plan
```bash
cd infra/terraform
terraform apply tfplan
```
Always use the saved plan file — never `terraform apply` (without `-auto-approve` and the plan file) as it regenerates the plan and may include drift.

### 3. Watch for errors
Common errors and fixes:

| Error | Fix |
|-------|-----|
| `BucketAlreadyExists` | Bucket name collision — change name in vars |
| `EntityAlreadyExists` (IAM) | IAM name collision — import or rename |
| `InvalidParameterException` | Check SSM parameter paths |
| `ThrottlingException` | Wait 30s, retry |
| `LockfileUnavailable` | Another apply in progress — check DynamoDB |

### 4. Verify key outputs
```bash
terraform output
```
Review outputs like `api_url`, `cloudfront_domain`, `s3_bucket_name`.

### 5. Smoke test
```bash
# Test the API endpoint
API_URL=$(terraform output -raw api_url)
curl -s "$API_URL/health" | jq .

# Verify CloudFront
CF_DOMAIN=$(terraform output -raw cloudfront_domain)
curl -I "https://$CF_DOMAIN" | head -3
```

### 6. Clean up plan file
```bash
rm infra/terraform/tfplan
```

## Rollback
Terraform doesn't have built-in rollback. Options:

1. **Write a new config** that reverts the change, then plan + apply
2. **Import and modify** if a resource was created incorrectly
3. **Manual AWS Console** for urgent production issues, then reconcile with `terraform import`

## State Backup
State is in S3 (`novakidlife-tfstate`) with versioning enabled.
To restore previous state:
```bash
aws s3api list-object-versions \
  --bucket novakidlife-tfstate \
  --prefix terraform.tfstate

aws s3api get-object \
  --bucket novakidlife-tfstate \
  --key terraform.tfstate \
  --version-id <version-id> \
  terraform.tfstate.backup
```
