# ── EventBridge ───────────────────────────────────────────────────────────────
#
# Daily scraper trigger:
#   cron(0 11 * * ? *) = 11:00 UTC = 6:00 AM EST (UTC-5) / 7:00 AM EDT (UTC-4)
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
