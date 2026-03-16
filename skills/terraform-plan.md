# Skill: Terraform Plan

**Purpose:** Safely review infrastructure changes before applying.

## Prerequisites
- AWS CLI configured
- Terraform >= 1.7 installed
- Backend initialized: `terraform init`
- DynamoDB lock table exists: `novakidlife-tflock`

## Steps

### 1. Navigate to infra
```bash
cd infra/terraform
```

### 2. Format check
```bash
terraform fmt -check -recursive
# If fails, auto-fix with: terraform fmt -recursive
```

### 3. Validate
```bash
terraform validate
```

### 4. Plan (save output)
```bash
terraform plan -out=tfplan 2>&1 | tee /tmp/terraform-plan.txt
```

### 5. Review the plan carefully

**Green (`+`)** — resources being created (usually safe)
**Yellow (`~`)** — resources being updated in-place (review carefully)
**Red (`-`)** — resources being destroyed (STOP and verify intent)
**Red/Green (`-/+`)** — resource replacement (destroy + recreate — check for data loss)

### High-Risk Changes to Escalate
- Any `aws_db_instance`, `aws_dynamodb_table` destroy
- `aws_s3_bucket` destroy (data loss)
- `aws_cloudfront_distribution` replacement (CDN downtime)
- IAM role/policy removals
- SQS queue deletions (in-flight messages lost)

### 6. Show plan summary
```bash
terraform show tfplan | grep -E "^  # |Plan:"
```

## What NOT to Run
- Never `terraform plan --destroy` without explicit intent
- Never `terraform plan -target` without understanding why
- Never skip `terraform validate` before plan

## State Inspection
```bash
# List all managed resources
terraform state list

# Show details of one resource
terraform state show aws_lambda_function.api
```

## Cost Estimate (optional)
If `infracost` is installed:
```bash
infracost breakdown --path . --terraform-plan-file tfplan
```
