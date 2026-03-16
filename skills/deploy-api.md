# Skill: Deploy API (Lambda)

**Purpose:** Package and deploy one or more Python Lambda functions.

## Prerequisites
- AWS CLI configured with deployment credentials
- Python 3.12 installed
- Target Lambda function exists (provisioned by Terraform)

## Deploy a Single Service

Replace `SERVICE` with one of: `api`, `events-scraper`, `image-gen`, `social-poster`, `scheduler`.

### 1. Install dependencies into package dir
```bash
SERVICE=api  # change as needed
cd services/$SERVICE

pip install -r requirements.txt \
  --target ./package \
  --platform mlinux_2_x86_64 \
  --implementation cp \
  --python-version 3.12 \
  --only-binary=:all: \
  --upgrade
```

### 2. Zip the package
```bash
cd package && zip -r ../deploy.zip . && cd ..
zip -g deploy.zip handler.py
# Add any additional source files:
# zip -g deploy.zip src/
```

### 3. Upload to Lambda
```bash
FUNCTION_NAME="novakidlife-${SERVICE}"

aws lambda update-function-code \
  --function-name "$FUNCTION_NAME" \
  --zip-file fileb://deploy.zip

aws lambda wait function-updated \
  --function-name "$FUNCTION_NAME"
```

### 4. Publish a version (prod)
```bash
aws lambda publish-version \
  --function-name "$FUNCTION_NAME" \
  --description "Deploy $(git rev-parse --short HEAD)"
```

### 5. Verify
```bash
aws lambda invoke \
  --function-name "$FUNCTION_NAME" \
  --payload '{"path":"/health","httpMethod":"GET"}' \
  /tmp/response.json && cat /tmp/response.json
```

### Cleanup
```bash
rm -rf package/ deploy.zip
```

## Deploy All Services
```bash
for svc in api events-scraper image-gen social-poster scheduler; do
  echo "Deploying $svc..."
  cd services/$svc
  # run steps 1-4 above
  cd ../..
done
```

## Rollback
```bash
# List versions
aws lambda list-versions-by-function --function-name novakidlife-api

# Point alias to previous version
aws lambda update-alias \
  --function-name novakidlife-api \
  --name live \
  --function-version <previous-version-number>
```
