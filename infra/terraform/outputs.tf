# ── Outputs ───────────────────────────────────────────────────────────────────
# These values are needed by CI/CD workflows (Session 10) and the deploy runbooks.

# ── CloudFront ────────────────────────────────────────────────────────────────

output "web_cloudfront_domain" {
  description = "CloudFront domain for the web distribution (CNAME this to novakidlife.com)"
  value       = aws_cloudfront_distribution.web.domain_name
}

output "web_cloudfront_distribution_id" {
  description = "Web CloudFront distribution ID (needed for cache invalidation)"
  value       = aws_cloudfront_distribution.web.id
}

output "media_cloudfront_domain" {
  description = "CloudFront domain for the media CDN (CNAME this to media.novakidlife.com)"
  value       = aws_cloudfront_distribution.media.domain_name
}

output "media_cloudfront_distribution_id" {
  description = "Media CloudFront distribution ID"
  value       = aws_cloudfront_distribution.media.id
}

# ── S3 ────────────────────────────────────────────────────────────────────────

output "web_bucket_name" {
  description = "S3 bucket name for the Next.js static export"
  value       = aws_s3_bucket.web.id
}

output "media_bucket_name" {
  description = "S3 bucket name for media assets (WebP images)"
  value       = aws_s3_bucket.media.id
}

# ── API Gateway ───────────────────────────────────────────────────────────────

output "api_invoke_url" {
  description = "API Gateway invoke URL (use before custom domain is configured)"
  value       = aws_api_gateway_stage.prod.invoke_url
}

output "api_custom_domain_target" {
  description = "Regional domain name to CNAME from api.novakidlife.com (null if cert not set)"
  value       = length(aws_api_gateway_domain_name.api) > 0 ? aws_api_gateway_domain_name.api[0].regional_domain_name : null
}

# ── Lambda ARNs ───────────────────────────────────────────────────────────────

output "lambda_api_arn" {
  description = "API Lambda ARN"
  value       = aws_lambda_function.api.arn
}

output "lambda_events_scraper_arn" {
  description = "Events scraper Lambda ARN"
  value       = aws_lambda_function.events_scraper.arn
}

output "lambda_image_gen_arn" {
  description = "Image gen Lambda ARN"
  value       = aws_lambda_function.image_gen.arn
}

# Social poster ARN output removed — Lambda deferred

# ── SQS ───────────────────────────────────────────────────────────────────────

output "events_queue_url" {
  description = "SQS events queue URL (used by scraper Lambda env var)"
  value       = aws_sqs_queue.events.url
}

output "events_queue_arn" {
  description = "SQS events queue ARN"
  value       = aws_sqs_queue.events.arn
}

output "social_queue_url" {
  description = "SQS social queue URL (used by scraper Lambda env var)"
  value       = aws_sqs_queue.social.url
}

output "social_queue_arn" {
  description = "SQS social queue ARN"
  value       = aws_sqs_queue.social.arn
}

output "events_dlq_arn" {
  description = "Events DLQ ARN"
  value       = aws_sqs_queue.events_dlq.arn
}

output "social_dlq_arn" {
  description = "Social DLQ ARN"
  value       = aws_sqs_queue.social_dlq.arn
}

# ── CloudWatch ────────────────────────────────────────────────────────────────

output "alarms_sns_topic_arn" {
  description = "SNS topic ARN for CloudWatch alarms"
  value       = aws_sns_topic.alarms.arn
}

output "dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}

# ── DNS CNAME records to create ───────────────────────────────────────────────

output "dns_records_to_create" {
  description = "DNS CNAME records to create in your domain registrar"
  value = {
    "novakidlife.com (ALIAS)"     = aws_cloudfront_distribution.web.domain_name
    "www.novakidlife.com (CNAME)" = aws_cloudfront_distribution.web.domain_name
    "media.novakidlife.com (CNAME)" = aws_cloudfront_distribution.media.domain_name
    "api.novakidlife.com (CNAME)" = length(aws_api_gateway_domain_name.api) > 0 ? aws_api_gateway_domain_name.api[0].regional_domain_name : "configure api_acm_certificate_arn first"
  }
}
