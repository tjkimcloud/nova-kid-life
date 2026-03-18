variable "aws_region" {
  description = "Primary AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "prod"
}

variable "project" {
  description = "Project identifier used in resource names and tags"
  type        = string
  default     = "novakidlife"
}

# ── Domains ──────────────────────────────────────────────────────────────────

variable "domain_name" {
  description = "Primary website domain (novakidlife.com)"
  type        = string
  default     = "novakidlife.com"
}

variable "www_domain_name" {
  description = "WWW domain alias"
  type        = string
  default     = "www.novakidlife.com"
}

variable "api_domain_name" {
  description = "API custom domain (api.novakidlife.com)"
  type        = string
  default     = "api.novakidlife.com"
}

variable "media_domain_name" {
  description = "Media CDN domain (media.novakidlife.com)"
  type        = string
  default     = "media.novakidlife.com"
}

# ── ACM certificates ─────────────────────────────────────────────────────────
# CloudFront requires certs in us-east-1 regardless of deployment region.
# Create these via AWS Console or a separate TF workspace before first apply:
#   aws acm request-certificate --domain-name novakidlife.com
#     --subject-alternative-names "*.novakidlife.com"
#     --validation-method DNS --region us-east-1

variable "web_acm_certificate_arn" {
  description = "ACM cert ARN for novakidlife.com (must be in us-east-1, used by CloudFront)"
  type        = string
  default     = ""
}

variable "api_acm_certificate_arn" {
  description = "ACM cert ARN for api.novakidlife.com (regional, used by API Gateway)"
  type        = string
  default     = ""
}

# ── Lambda ────────────────────────────────────────────────────────────────────

variable "lambda_runtime" {
  description = "Python runtime for all Lambda functions"
  type        = string
  default     = "python3.12"
}

variable "api_lambda_memory" {
  description = "Memory (MB) for API Lambda"
  type        = number
  default     = 256
}

variable "api_lambda_timeout" {
  description = "Timeout (s) for API Lambda"
  type        = number
  default     = 30
}

variable "scraper_lambda_memory" {
  description = "Memory (MB) for events-scraper Lambda"
  type        = number
  default     = 1024
}

variable "scraper_lambda_timeout" {
  description = "Timeout (s) for events-scraper Lambda (max 900)"
  type        = number
  default     = 900
}

variable "image_gen_lambda_memory" {
  description = "Memory (MB) for image-gen Lambda"
  type        = number
  default     = 512
}

variable "image_gen_lambda_timeout" {
  description = "Timeout (s) for image-gen Lambda"
  type        = number
  default     = 300
}

variable "social_poster_lambda_memory" {
  description = "Memory (MB) for social-poster Lambda"
  type        = number
  default     = 256
}

variable "social_poster_lambda_timeout" {
  description = "Timeout (s) for social-poster Lambda"
  type        = number
  default     = 120
}

variable "content_generator_lambda_memory" {
  description = "Memory (MB) for content-generator Lambda"
  type        = number
  default     = 512
}

variable "content_generator_lambda_timeout" {
  description = "Timeout (s) for content-generator Lambda"
  type        = number
  default     = 300
}

# ── SQS ───────────────────────────────────────────────────────────────────────

variable "sqs_message_retention_seconds" {
  description = "SQS message retention period (seconds)"
  type        = number
  default     = 345600 # 4 days
}

variable "sqs_visibility_timeout_seconds" {
  description = "SQS visibility timeout — must be >= Lambda timeout"
  type        = number
  default     = 900
}

variable "dlq_max_receive_count" {
  description = "Times a message is delivered before moving to DLQ"
  type        = number
  default     = 3
}

# ── CloudWatch ────────────────────────────────────────────────────────────────

variable "alarm_email" {
  description = "Email address for CloudWatch alarm SNS notifications"
  type        = string
  default     = ""
}

variable "lambda_error_threshold" {
  description = "Lambda error count threshold per 5-minute window to trigger alarm"
  type        = number
  default     = 5
}

variable "dlq_depth_threshold" {
  description = "DLQ message count threshold to trigger alarm"
  type        = number
  default     = 1
}

# ── EventBridge ───────────────────────────────────────────────────────────────

variable "scraper_schedule" {
  description = "EventBridge cron for daily scraper (UTC). Default = 11:00 UTC = 6:00 AM EST"
  type        = string
  default     = "cron(0 11 * * ? *)"
}

variable "content_generator_weekend_schedule" {
  description = "EventBridge cron for weekend roundup generator (UTC). Default = Fri 01:00 UTC = Thu 8pm EST"
  type        = string
  default     = "cron(0 1 ? * FRI *)"
}

variable "content_generator_week_ahead_schedule" {
  description = "EventBridge cron for week-ahead guide generator (UTC). Default = Mon 11:00 UTC = Mon 6am EST"
  type        = string
  default     = "cron(0 11 ? * MON *)"
}
