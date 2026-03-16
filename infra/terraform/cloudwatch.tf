# ── CloudWatch ────────────────────────────────────────────────────────────────
#
# Resources:
#   SNS topic + email subscription  — alarm notifications
#   Lambda log groups               — 5 functions, 30-day retention
#   Lambda error alarms             — 5 functions
#   Lambda duration alarms          — scraper + image-gen (long-running)
#   SQS DLQ depth alarms            — events-dlq + social-dlq
#   API Gateway 5xx alarm           — API error rate
#   Dashboard                       — unified ops view

# ── SNS ───────────────────────────────────────────────────────────────────────

resource "aws_sns_topic" "alarms" {
  name = "${local.name_prefix}-alarms"
}

resource "aws_sns_topic_subscription" "email" {
  count     = var.alarm_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alarms.arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

# ── Lambda log groups ─────────────────────────────────────────────────────────

resource "aws_cloudwatch_log_group" "lambda_api" {
  name              = "/aws/lambda/${aws_lambda_function.api.function_name}"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "lambda_events_scraper" {
  name              = "/aws/lambda/${aws_lambda_function.events_scraper.function_name}"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "lambda_image_gen" {
  name              = "/aws/lambda/${aws_lambda_function.image_gen.function_name}"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "lambda_social_poster" {
  name              = "/aws/lambda/${aws_lambda_function.social_poster.function_name}"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "lambda_scheduler" {
  name              = "/aws/lambda/${aws_lambda_function.scheduler.function_name}"
  retention_in_days = 14
}

# ── Lambda error alarms ───────────────────────────────────────────────────────

locals {
  lambda_functions = {
    api            = aws_lambda_function.api.function_name
    events_scraper = aws_lambda_function.events_scraper.function_name
    image_gen      = aws_lambda_function.image_gen.function_name
    social_poster  = aws_lambda_function.social_poster.function_name
    scheduler      = aws_lambda_function.scheduler.function_name
  }
}

resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  for_each = local.lambda_functions

  alarm_name          = "${local.name_prefix}-${each.key}-errors"
  alarm_description   = "Lambda ${each.value} error count exceeded threshold"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = var.lambda_error_threshold
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = each.value
  }

  alarm_actions = [aws_sns_topic.alarms.arn]
  ok_actions    = [aws_sns_topic.alarms.arn]
}

# ── Lambda duration alarms (long-running functions) ───────────────────────────

resource "aws_cloudwatch_metric_alarm" "scraper_duration" {
  alarm_name          = "${local.name_prefix}-events-scraper-duration"
  alarm_description   = "events-scraper approaching timeout (>800s)"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 900
  statistic           = "Maximum"
  threshold           = 800000 # milliseconds
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.events_scraper.function_name
  }

  alarm_actions = [aws_sns_topic.alarms.arn]
}

resource "aws_cloudwatch_metric_alarm" "image_gen_duration" {
  alarm_name          = "${local.name_prefix}-image-gen-duration"
  alarm_description   = "image-gen approaching timeout (>250s)"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Maximum"
  threshold           = 250000
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.image_gen.function_name
  }

  alarm_actions = [aws_sns_topic.alarms.arn]
}

# ── SQS DLQ depth alarms ──────────────────────────────────────────────────────

resource "aws_cloudwatch_metric_alarm" "events_dlq_depth" {
  alarm_name          = "${local.name_prefix}-events-dlq-depth"
  alarm_description   = "Messages in events DLQ — image-gen failures"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Maximum"
  threshold           = var.dlq_depth_threshold
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = aws_sqs_queue.events_dlq.name
  }

  alarm_actions = [aws_sns_topic.alarms.arn]
  ok_actions    = [aws_sns_topic.alarms.arn]
}

resource "aws_cloudwatch_metric_alarm" "social_dlq_depth" {
  alarm_name          = "${local.name_prefix}-social-dlq-depth"
  alarm_description   = "Messages in social DLQ — social-poster failures"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Maximum"
  threshold           = var.dlq_depth_threshold
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = aws_sqs_queue.social_dlq.name
  }

  alarm_actions = [aws_sns_topic.alarms.arn]
  ok_actions    = [aws_sns_topic.alarms.arn]
}

# ── API Gateway 5xx alarm ─────────────────────────────────────────────────────

resource "aws_cloudwatch_metric_alarm" "apigw_5xx" {
  alarm_name          = "${local.name_prefix}-apigw-5xx"
  alarm_description   = "API Gateway 5xx error rate elevated"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "5XXError"
  namespace           = "AWS/ApiGateway"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  treat_missing_data  = "notBreaching"

  dimensions = {
    ApiName = aws_api_gateway_rest_api.main.name
    Stage   = var.environment
  }

  alarm_actions = [aws_sns_topic.alarms.arn]
}

# ── CloudWatch Dashboard ──────────────────────────────────────────────────────

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${local.name_prefix}-ops"

  dashboard_body = jsonencode({
    widgets = [
      # Row 1: Lambda invocations + errors
      {
        type   = "metric"
        x      = 0; y = 0; width = 12; height = 6
        properties = {
          title  = "Lambda Invocations"
          period = 300
          stat   = "Sum"
          metrics = [
            ["AWS/Lambda", "Invocations", "FunctionName", aws_lambda_function.api.function_name],
            ["AWS/Lambda", "Invocations", "FunctionName", aws_lambda_function.events_scraper.function_name],
            ["AWS/Lambda", "Invocations", "FunctionName", aws_lambda_function.image_gen.function_name],
            ["AWS/Lambda", "Invocations", "FunctionName", aws_lambda_function.social_poster.function_name],
          ]
        }
      },
      {
        type   = "metric"
        x      = 12; y = 0; width = 12; height = 6
        properties = {
          title  = "Lambda Errors"
          period = 300
          stat   = "Sum"
          metrics = [
            ["AWS/Lambda", "Errors", "FunctionName", aws_lambda_function.api.function_name],
            ["AWS/Lambda", "Errors", "FunctionName", aws_lambda_function.events_scraper.function_name],
            ["AWS/Lambda", "Errors", "FunctionName", aws_lambda_function.image_gen.function_name],
            ["AWS/Lambda", "Errors", "FunctionName", aws_lambda_function.social_poster.function_name],
          ]
        }
      },
      # Row 2: Lambda duration
      {
        type   = "metric"
        x      = 0; y = 6; width = 12; height = 6
        properties = {
          title  = "Lambda Duration (ms)"
          period = 300
          stat   = "Average"
          metrics = [
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.api.function_name],
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.events_scraper.function_name],
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.image_gen.function_name],
          ]
        }
      },
      # Row 2: SQS queue depths
      {
        type   = "metric"
        x      = 12; y = 6; width = 12; height = 6
        properties = {
          title  = "SQS Queue Depth"
          period = 300
          stat   = "Maximum"
          metrics = [
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", aws_sqs_queue.events.name],
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", aws_sqs_queue.social.name],
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", aws_sqs_queue.events_dlq.name, { color = "#d62728" }],
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", aws_sqs_queue.social_dlq.name, { color = "#e377c2" }],
          ]
        }
      },
      # Row 3: API Gateway
      {
        type   = "metric"
        x      = 0; y = 12; width = 12; height = 6
        properties = {
          title  = "API Gateway Requests"
          period = 300
          stat   = "Sum"
          metrics = [
            ["AWS/ApiGateway", "Count", "ApiName", aws_api_gateway_rest_api.main.name, "Stage", var.environment],
            ["AWS/ApiGateway", "4XXError", "ApiName", aws_api_gateway_rest_api.main.name, "Stage", var.environment],
            ["AWS/ApiGateway", "5XXError", "ApiName", aws_api_gateway_rest_api.main.name, "Stage", var.environment],
          ]
        }
      },
      {
        type   = "metric"
        x      = 12; y = 12; width = 12; height = 6
        properties = {
          title  = "API Gateway Latency (ms)"
          period = 300
          stat   = "p99"
          metrics = [
            ["AWS/ApiGateway", "Latency", "ApiName", aws_api_gateway_rest_api.main.name, "Stage", var.environment],
            ["AWS/ApiGateway", "IntegrationLatency", "ApiName", aws_api_gateway_rest_api.main.name, "Stage", var.environment],
          ]
        }
      },
    ]
  })
}
