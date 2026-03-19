#!/usr/bin/env bash
# Deploy all Lambda functions to AWS
# Usage: bash scripts/deploy-lambdas.sh
# Run from repo root

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SERVICES_DIR="$REPO_ROOT/services"
AWS_PROFILE="${AWS_PROFILE:-default}"
REGION="us-east-1"
ENV="prod"

deploy_service() {
  local svc=$1
  local src_files=("${@:2}")
  local function_name="novakidlife-${ENV}-${svc}"
  local svc_dir="$SERVICES_DIR/$svc"

  echo ""
  echo "==> Deploying $svc..."
  cd "$svc_dir"

  # Clean up previous build
  rm -rf package deploy.zip

  # Install dependencies for Linux Lambda
  echo "    Installing dependencies..."
  pip install -r requirements.txt \
    --target ./package \
    --platform manylinux2014_x86_64 \
    --implementation cp \
    --python-version 3.12 \
    --only-binary=:all: \
    --upgrade \
    --quiet

  # Zip dependencies
  echo "    Zipping..."
  cd package && zip -r ../deploy.zip . -x "*.pyc" -x "*/__pycache__/*" > /dev/null && cd ..

  # Add source files
  for f in "${src_files[@]}"; do
    if [ -e "$f" ]; then
      zip -gr deploy.zip "$f" -x "*.pyc" -x "*/__pycache__/*" -x "tests/*" > /dev/null
    fi
  done

  # Upload to Lambda
  echo "    Uploading to $function_name..."
  aws lambda update-function-code \
    --function-name "$function_name" \
    --zip-file fileb://deploy.zip \
    --profile "$AWS_PROFILE" \
    --region "$REGION" \
    --output text --query 'CodeSize' | xargs -I{} echo "    Code size: {} bytes"

  aws lambda wait function-updated \
    --function-name "$function_name" \
    --profile "$AWS_PROFILE" \
    --region "$REGION"

  # Clean up
  rm -rf package deploy.zip
  echo "    Done: $svc"
  cd "$REPO_ROOT"
}

# Deploy each service with its source files
deploy_service "api" handler.py db.py models.py router.py routes/
deploy_service "events-scraper" handler.py config/ scrapers/
deploy_service "image-gen" handler.py alt_text.py enhancer.py generator.py processor.py prompts.py sourcer.py uploader.py

echo ""
echo "All Lambda functions deployed successfully."
