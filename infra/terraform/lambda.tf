# ── Lambda Functions ──────────────────────────────────────────────────────────
#
# Six functions:
#   novakidlife-api            REST API (API Gateway proxy)
#   novakidlife-events-scraper Daily 3-tier scraper (EventBridge trigger)
#   novakidlife-quality-agent  Post-scrape quality filter + source scorecard
#   novakidlife-image-gen      Image pipeline (SQS trigger from events-queue)
#   novakidlife-social-poster  Buffer API poster (SQS trigger from social-queue)
#   novakidlife-scheduler      EventBridge stub (reserved for future orchestration)
#
# DEPLOYMENT NOTE: These archives zip raw source only (no pip dependencies).
# CI/CD (Session 10 deploy-api.yml) runs `pip install -r requirements.txt -t`
# into the archive before uploading. Terraform manages function config;
# CI/CD manages the actual deployment package.

# ── builds/ directory placeholder ─────────────────────────────────────────────
# `terraform apply` will create zip files here. Add infra/terraform/builds/ to .gitignore.

# ── Deployment archives ───────────────────────────────────────────────────────

data "archive_file" "api" {
  type        = "zip"
  source_dir  = "${local.service_path}/api"
  output_path = "${local.builds_path}/api.zip"
  excludes    = ["__pycache__", "*.pyc", ".env", "tests", ".pytest_cache"]
}

data "archive_file" "events_scraper" {
  type        = "zip"
  source_dir  = "${local.service_path}/events-scraper"
  output_path = "${local.builds_path}/events-scraper.zip"
  excludes    = ["__pycache__", "*.pyc", ".env", "tests", ".pytest_cache"]
}

data "archive_file" "image_gen" {
  type        = "zip"
  source_dir  = "${local.service_path}/image-gen"
  output_path = "${local.builds_path}/image-gen.zip"
  excludes    = ["__pycache__", "*.pyc", ".env", "tests", ".pytest_cache"]
}

# Placeholder archives for services not yet implemented (Session 8)
data "archive_file" "social_poster" {
  type        = "zip"
  source_dir  = "${local.service_path}/social-poster"
  output_path = "${local.builds_path}/social-poster.zip"
  excludes    = ["__pycache__", "*.pyc", ".env", "tests", ".pytest_cache"]
}

data "archive_file" "scheduler" {
  type        = "zip"
  source_dir  = "${local.service_path}/scheduler"
  output_path = "${local.builds_path}/scheduler.zip"
  excludes    = ["__pycache__", "*.pyc", ".env", "tests", ".pytest_cache"]
}

data "archive_file" "content_generator" {
  type        = "zip"
  source_dir  = "${local.service_path}/content-generator"
  output_path = "${local.builds_path}/content-generator.zip"
  excludes    = ["__pycache__", "*.pyc", ".env", "tests", ".pytest_cache"]
}

data "archive_file" "quality_agent" {
  type        = "zip"
  source_dir  = "${local.service_path}/quality-agent"
  output_path = "${local.builds_path}/quality-agent.zip"
  excludes    = ["__pycache__", "*.pyc", ".env", "tests", ".pytest_cache"]
}

# ── Shared IAM assume-role policy ─────────────────────────────────────────────

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# ── Helper: SSM read policy for /novakidlife/* ────────────────────────────────

data "aws_iam_policy_document" "ssm_read" {
  statement {
    effect    = "Allow"
    actions   = ["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParametersByPath"]
    resources = ["arn:aws:ssm:${var.aws_region}:*:parameter/novakidlife/*"]
  }
}

resource "aws_iam_policy" "ssm_read" {
  name        = "${local.name_prefix}-ssm-read"
  description = "Allow Lambda functions to read /novakidlife/* SSM parameters"
  policy      = data.aws_iam_policy_document.ssm_read.json
}

# ── API Lambda ────────────────────────────────────────────────────────────────

resource "aws_iam_role" "api" {
  name               = "${local.name_prefix}-api-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "api_basic_execution" {
  role       = aws_iam_role.api.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "api_ssm" {
  role       = aws_iam_role.api.name
  policy_arn = aws_iam_policy.ssm_read.arn
}

resource "aws_lambda_function" "api" {
  function_name    = "${local.name_prefix}-api"
  description      = "NovaKidLife REST API — 15 endpoints"
  role             = aws_iam_role.api.arn
  runtime          = var.lambda_runtime
  handler          = "handler.handler"
  filename         = data.archive_file.api.output_path
  source_code_hash = data.archive_file.api.output_base64sha256
  memory_size      = var.api_lambda_memory
  timeout          = var.api_lambda_timeout

  environment {
    variables = {
      ENVIRONMENT           = var.environment
      SSM_PREFIX            = "/novakidlife"
      SUPABASE_URL_PARAM    = "/novakidlife/supabase/url"
      SUPABASE_KEY_PARAM    = "/novakidlife/supabase/service-key"
      OPENAI_API_KEY_PARAM  = "/novakidlife/openai/api-key"
      ADMIN_API_KEY_PARAM   = "/novakidlife/admin/api-key"
      SCRAPER_FUNCTION_NAME = aws_lambda_function.events_scraper.function_name
    }
  }

  depends_on = [aws_iam_role_policy_attachment.api_basic_execution]
}

# Allow API Lambda to invoke events-scraper (for /admin/events/trigger-scrape)
data "aws_iam_policy_document" "api_invoke_scraper" {
  statement {
    effect    = "Allow"
    actions   = ["lambda:InvokeFunction"]
    resources = [aws_lambda_function.events_scraper.arn]
  }
}

resource "aws_iam_role_policy" "api_invoke_scraper" {
  name   = "invoke-scraper"
  role   = aws_iam_role.api.id
  policy = data.aws_iam_policy_document.api_invoke_scraper.json
}

# ── Events Scraper Lambda ──────────────────────────────────────────────────────

resource "aws_iam_role" "events_scraper" {
  name               = "${local.name_prefix}-events-scraper-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "events_scraper_basic_execution" {
  role       = aws_iam_role.events_scraper.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "events_scraper_ssm" {
  role       = aws_iam_role.events_scraper.name
  policy_arn = aws_iam_policy.ssm_read.arn
}

data "aws_iam_policy_document" "events_scraper_sqs" {
  statement {
    effect = "Allow"
    actions = [
      "sqs:SendMessage",
      "sqs:GetQueueUrl",
      "sqs:GetQueueAttributes"
    ]
    resources = [
      aws_sqs_queue.events.arn,
      aws_sqs_queue.social.arn
    ]
  }
}

resource "aws_iam_role_policy" "events_scraper_sqs" {
  name   = "sqs-publish"
  role   = aws_iam_role.events_scraper.id
  policy = data.aws_iam_policy_document.events_scraper_sqs.json
}

resource "aws_lambda_function" "events_scraper" {
  function_name    = "${local.name_prefix}-events-scraper"
  description      = "3-tier event scraper — 59 sources, daily via EventBridge"
  role             = aws_iam_role.events_scraper.arn
  runtime          = var.lambda_runtime
  handler          = "handler.handler"
  filename         = data.archive_file.events_scraper.output_path
  source_code_hash = data.archive_file.events_scraper.output_base64sha256
  memory_size      = var.scraper_lambda_memory
  timeout          = var.scraper_lambda_timeout

  environment {
    variables = {
      ENVIRONMENT              = var.environment
      SSM_PREFIX               = "/novakidlife"
      SUPABASE_URL_PARAM       = "/novakidlife/supabase/url"
      SUPABASE_KEY_PARAM       = "/novakidlife/supabase/service-key"
      OPENAI_API_KEY_PARAM     = "/novakidlife/openai/api-key"
      MEETUP_CLIENT_ID_PARAM   = "/novakidlife/meetup/client-id"
      MEETUP_SECRET_PARAM      = "/novakidlife/meetup/client-secret"
      EVENTS_QUEUE_URL         = aws_sqs_queue.events.url
      SOCIAL_QUEUE_URL         = aws_sqs_queue.social.url
    }
  }

  depends_on = [aws_iam_role_policy_attachment.events_scraper_basic_execution]
}

# ── Image Gen Lambda ──────────────────────────────────────────────────────────

resource "aws_iam_role" "image_gen" {
  name               = "${local.name_prefix}-image-gen-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "image_gen_basic_execution" {
  role       = aws_iam_role.image_gen.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "image_gen_ssm" {
  role       = aws_iam_role.image_gen.name
  policy_arn = aws_iam_policy.ssm_read.arn
}

# SQS consume from events-queue + VPC-optional execution
resource "aws_iam_role_policy_attachment" "image_gen_sqs_execution" {
  role       = aws_iam_role.image_gen.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole"
}

data "aws_iam_policy_document" "image_gen_s3" {
  statement {
    effect    = "Allow"
    actions   = ["s3:PutObject", "s3:PutObjectAcl", "s3:GetObject", "s3:HeadObject"]
    resources = ["${aws_s3_bucket.media.arn}/*"]
  }
  statement {
    effect    = "Allow"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.media.arn]
  }
}

resource "aws_iam_role_policy" "image_gen_s3" {
  name   = "s3-media-write"
  role   = aws_iam_role.image_gen.id
  policy = data.aws_iam_policy_document.image_gen_s3.json
}

resource "aws_lambda_function" "image_gen" {
  function_name    = "${local.name_prefix}-image-gen"
  description      = "AI image generation pipeline — Imagen 3 → DALL-E 3 fallback"
  role             = aws_iam_role.image_gen.arn
  runtime          = var.lambda_runtime
  handler          = "handler.handler"
  filename         = data.archive_file.image_gen.output_path
  source_code_hash = data.archive_file.image_gen.output_base64sha256
  memory_size      = var.image_gen_lambda_memory
  timeout          = var.image_gen_lambda_timeout

  environment {
    variables = {
      ENVIRONMENT                   = var.environment
      SSM_PREFIX                    = "/novakidlife"
      SUPABASE_URL_PARAM            = "/novakidlife/supabase/url"
      SUPABASE_KEY_PARAM            = "/novakidlife/supabase/service-key"
      OPENAI_API_KEY_PARAM          = "/novakidlife/openai/api-key"
      GOOGLE_PROJECT_ID_PARAM       = "/novakidlife/google/project-id"
      GOOGLE_LOCATION_PARAM         = "/novakidlife/google/location"
      GOOGLE_SA_JSON_PARAM          = "/novakidlife/google/service-account-json"
      GOOGLE_PLACES_API_KEY_PARAM   = "/novakidlife/google/places-api-key"
      UNSPLASH_ACCESS_KEY_PARAM     = "/novakidlife/unsplash/access-key"
      PEXELS_API_KEY_PARAM          = "/novakidlife/pexels/api-key"
      MEDIA_BUCKET_NAME             = aws_s3_bucket.media.id
      MEDIA_CDN_URL                 = "https://${var.media_domain_name}"
    }
  }

  depends_on = [aws_iam_role_policy_attachment.image_gen_basic_execution]
}

# Event source mapping: events-queue → image-gen
resource "aws_lambda_event_source_mapping" "events_to_image_gen" {
  event_source_arn                   = aws_sqs_queue.events.arn
  function_name                      = aws_lambda_function.image_gen.arn
  batch_size                         = 1
  maximum_batching_window_in_seconds = 0
  enabled                            = true

  function_response_types = ["ReportBatchItemFailures"]
}

# ── Content Generator Lambda ──────────────────────────────────────────────────

resource "aws_iam_role" "content_generator" {
  name               = "${local.name_prefix}-content-generator-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "content_generator_basic_execution" {
  role       = aws_iam_role.content_generator.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "content_generator_ssm" {
  role       = aws_iam_role.content_generator.name
  policy_arn = aws_iam_policy.ssm_read.arn
}

resource "aws_lambda_function" "content_generator" {
  function_name    = "${local.name_prefix}-content-generator"
  description      = "Blog post generator — GPT-4o-mini weekend/week-ahead roundups"
  role             = aws_iam_role.content_generator.arn
  runtime          = var.lambda_runtime
  handler          = "handler.handler"
  filename         = data.archive_file.content_generator.output_path
  source_code_hash = data.archive_file.content_generator.output_base64sha256
  memory_size      = var.content_generator_lambda_memory
  timeout          = var.content_generator_lambda_timeout

  environment {
    variables = {
      ENVIRONMENT              = var.environment
      SSM_PREFIX               = "/novakidlife"
      SUPABASE_URL_PARAM       = "/novakidlife/supabase/url"
      SUPABASE_KEY_PARAM       = "/novakidlife/supabase/service-key"
      OPENAI_API_KEY_PARAM     = "/novakidlife/openai/api-key"
      GITHUB_TOKEN_PARAM       = "/novakidlife/github/token"
      GITHUB_REPO              = "novakidlife/novakidlife"
      DEPLOY_WORKFLOW          = "deploy-frontend.yml"
    }
  }

  depends_on = [aws_iam_role_policy_attachment.content_generator_basic_execution]
}

# Allow EventBridge to invoke content-generator (weekend trigger)
resource "aws_lambda_permission" "eventbridge_invoke_content_generator_weekend" {
  statement_id  = "AllowEventBridgeInvokeWeekend"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.content_generator.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.content_generator_weekend.arn
}

# Allow EventBridge to invoke content-generator (week-ahead trigger)
resource "aws_lambda_permission" "eventbridge_invoke_content_generator_week_ahead" {
  statement_id  = "AllowEventBridgeInvokeWeekAhead"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.content_generator.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.content_generator_week_ahead.arn
}

# ── Social Poster Lambda ──────────────────────────────────────────────────────
# Deferred — social posting via direct platform APIs when ready (no Ayrshare cost).
# SQS social queue stays active (scraper writes to it). Lambda re-added in future session.
# To re-enable: uncomment this block and run terraform apply.

# ── Scheduler Lambda ──────────────────────────────────────────────────────────
# Stub function — EventBridge targets events-scraper directly.
# Reserved for future multi-step orchestration (e.g. fan-out, rate control).

resource "aws_iam_role" "scheduler" {
  name               = "${local.name_prefix}-scheduler-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "scheduler_basic_execution" {
  role       = aws_iam_role.scheduler.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "scheduler" {
  function_name    = "${local.name_prefix}-scheduler"
  description      = "EventBridge trigger stub — future orchestration"
  role             = aws_iam_role.scheduler.arn
  runtime          = var.lambda_runtime
  handler          = "handler.handler"
  filename         = data.archive_file.scheduler.output_path
  source_code_hash = data.archive_file.scheduler.output_base64sha256
  memory_size      = 128
  timeout          = 60

  environment {
    variables = {
      ENVIRONMENT = var.environment
    }
  }

  depends_on = [aws_iam_role_policy_attachment.scheduler_basic_execution]
}

# ── Lambda permissions ─────────────────────────────────────────────────────────

# Allow API Gateway to invoke api Lambda
resource "aws_lambda_permission" "apigw_invoke_api" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.main.execution_arn}/*/*"
}

# Allow EventBridge to invoke events-scraper Lambda
resource "aws_lambda_permission" "eventbridge_invoke_scraper" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.events_scraper.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_scraper.arn
}

# ── Quality Agent Lambda ──────────────────────────────────────────────────────
# Post-scrape event filter: removes off-geography events, scores sources,
# maintains scraper_metrics feedback loop. Runs 15 min after scraper.

resource "aws_iam_role" "quality_agent" {
  name               = "${local.name_prefix}-quality-agent-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "quality_agent_basic_execution" {
  role       = aws_iam_role.quality_agent.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "quality_agent_ssm" {
  role       = aws_iam_role.quality_agent.name
  policy_arn = aws_iam_policy.ssm_read.arn
}

resource "aws_cloudwatch_log_group" "lambda_quality_agent" {
  name              = "/aws/lambda/${local.name_prefix}-quality-agent"
  retention_in_days = 14
}

resource "aws_lambda_function" "quality_agent" {
  function_name    = "${local.name_prefix}-quality-agent"
  description      = "Post-scrape quality filter — removes off-NoVA events, scores sources"
  role             = aws_iam_role.quality_agent.arn
  runtime          = var.lambda_runtime
  handler          = "handler.handler"
  filename         = data.archive_file.quality_agent.output_path
  source_code_hash = data.archive_file.quality_agent.output_base64sha256
  memory_size      = 512
  timeout          = 300

  environment {
    variables = {
      ENVIRONMENT              = var.environment
      SSM_PREFIX               = "/novakidlife"
      SUPABASE_URL_PARAM       = "/novakidlife/supabase/url"
      SUPABASE_KEY_PARAM       = "/novakidlife/supabase/service-key"
      OPENAI_API_KEY_PARAM     = "/novakidlife/openai/api-key"
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.quality_agent_basic_execution,
    aws_cloudwatch_log_group.lambda_quality_agent,
  ]
}

resource "aws_lambda_permission" "eventbridge_invoke_quality_agent" {
  statement_id  = "AllowEventBridgeInvokeQualityAgent"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.quality_agent.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.quality_agent.arn
}
