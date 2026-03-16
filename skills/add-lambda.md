# Skill: Add Lambda Function

**Purpose:** Scaffold a new Python 3.12 Lambda service following project conventions.

## Service Directory Structure

```
services/<service-name>/
├── handler.py          # Lambda entry point
├── requirements.txt    # Runtime dependencies
├── requirements-dev.txt # Test/lint dependencies
├── package.json        # npm scripts for tooling
└── tests/
    ├── __init__.py
    └── test_handler.py
```

## handler.py Template

```python
"""
<service-name> Lambda handler.
Triggered by: <SQS / EventBridge / API Gateway / etc.>
"""
from __future__ import annotations

import json
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event: dict, context) -> dict:
    """Lambda entry point."""
    logger.info("Event received: %s", json.dumps(event))

    try:
        result = process(event)
        return {"statusCode": 200, "body": json.dumps(result)}
    except Exception as exc:
        logger.exception("Unhandled error: %s", exc)
        raise  # Re-raise so Lambda marks invocation as failed (SQS retry / DLQ)


def process(event: dict) -> dict:
    """Core business logic."""
    # TODO: implement
    return {"status": "ok"}
```

## requirements.txt Template

```
boto3>=1.34
supabase>=2.0
```

## requirements-dev.txt Template

```
pytest>=8.0
pytest-asyncio>=0.23
ruff>=0.4
moto[s3,sqs]>=5.0
```

## Steps

1. Create the directory: `mkdir -p services/<name>/tests`
2. Create `handler.py` from template above
3. Create `requirements.txt` with needed dependencies
4. Create `requirements-dev.txt` with dev dependencies
5. Create `tests/__init__.py` (empty)
6. Create `tests/test_handler.py` with at least one smoke test
7. Add Terraform resource in `infra/terraform/lambdas.tf`

## Terraform Resource Snippet

```hcl
resource "aws_lambda_function" "service_name" {
  function_name = "novakidlife-service-name"
  role          = aws_iam_role.lambda_exec.arn
  runtime       = "python3.12"
  handler       = "handler.handler"
  filename      = "../../services/service-name/deploy.zip"

  environment {
    variables = {
      SUPABASE_URL = var.supabase_url
    }
  }

  tags = {
    project = "novakidlife"
    env     = "prod"
  }
}
```

## SQS Trigger Snippet

```hcl
resource "aws_lambda_event_source_mapping" "service_name_sqs" {
  event_source_arn = aws_sqs_queue.service_name_queue.arn
  function_name    = aws_lambda_function.service_name.arn
  batch_size       = 10
}
```
