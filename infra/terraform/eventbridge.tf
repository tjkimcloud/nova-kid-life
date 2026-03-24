# ── EventBridge ───────────────────────────────────────────────────────────────
#
# Weekly scraper trigger:
#   cron(0 11 ? * WED *) = Wednesday 11:00 UTC = Wednesday 6:00 AM EST (UTC-5)
#
# Weekly cadence: scrape Wed → image-gen processes queue → content-gen Thu 8pm
# triggers deploy-frontend → site rebuilt with fresh events by Friday morning.
#
# EventBridge → events-scraper Lambda directly.
# Lambda permission for EventBridge is defined in lambda.tf.

resource "aws_cloudwatch_event_rule" "daily_scraper" {
  name                = "${local.name_prefix}-daily-scraper"
  description         = "Trigger events-scraper Lambda daily at 6am EST"
  schedule_expression = var.scraper_schedule
  state               = "ENABLED"
}

resource "aws_cloudwatch_event_target" "daily_scraper" {
  rule      = aws_cloudwatch_event_rule.daily_scraper.name
  target_id = "EventsScraperLambda"
  arn       = aws_lambda_function.events_scraper.arn

  # Pass context to the Lambda so it knows it's a scheduled run
  input = jsonencode({
    source    = "eventbridge.scheduled"
    detail    = "daily-scrape"
    tiers     = ["tier1", "tier2", "tier3", "pokemon"]
  })
}

# ── Content Generator schedules ────────────────────────────────────────────────
#
# Weekend roundup: Thursday 8:00 PM EST = Friday 01:00 UTC
#   cron(0 1 ? * FRI *) — fires every Friday at 01:00 UTC
#
# Week-ahead guide: Monday 6:00 AM EST = Monday 11:00 UTC
#   cron(0 11 ? * MON *) — fires every Monday at 11:00 UTC

resource "aws_cloudwatch_event_rule" "content_generator_weekend" {
  name                = "${local.name_prefix}-content-generator-weekend"
  description         = "Trigger content-generator for weekend roundup (Thu 8pm EST = Fri 01:00 UTC)"
  schedule_expression = var.content_generator_weekend_schedule
  state               = "ENABLED"
}

resource "aws_cloudwatch_event_target" "content_generator_weekend" {
  rule      = aws_cloudwatch_event_rule.content_generator_weekend.name
  target_id = "ContentGeneratorWeekend"
  arn       = aws_lambda_function.content_generator.arn

  input = jsonencode({
    trigger = "weekend"
  })
}

resource "aws_cloudwatch_event_rule" "content_generator_week_ahead" {
  name                = "${local.name_prefix}-content-generator-week-ahead"
  description         = "Trigger content-generator for week-ahead guide (Mon 6am EST = Mon 11:00 UTC)"
  schedule_expression = var.content_generator_week_ahead_schedule
  state               = "ENABLED"
}

resource "aws_cloudwatch_event_target" "content_generator_week_ahead" {
  rule      = aws_cloudwatch_event_rule.content_generator_week_ahead.name
  target_id = "ContentGeneratorWeekAhead"
  arn       = aws_lambda_function.content_generator.arn

  input = jsonencode({
    trigger = "week_ahead"
  })
}
