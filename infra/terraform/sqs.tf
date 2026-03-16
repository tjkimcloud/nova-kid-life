# ── SQS Queues ────────────────────────────────────────────────────────────────
#
# Four queues (2 main + 2 DLQs):
#   novakidlife-events-dlq     DLQ for events pipeline
#   novakidlife-events-queue   Events pipeline → image-gen Lambda
#   novakidlife-social-dlq     DLQ for social pipeline
#   novakidlife-social-queue   Social pipeline → social-poster Lambda
#
# Scraper publishes to both events-queue and social-queue on new events.
# DLQs receive messages after var.dlq_max_receive_count failed attempts.

# ── Events DLQ ────────────────────────────────────────────────────────────────

resource "aws_sqs_queue" "events_dlq" {
  name                       = "${local.name_prefix}-events-dlq"
  message_retention_seconds  = 1209600 # 14 days — longer retention for dead letters
  visibility_timeout_seconds = 30
  kms_master_key_id          = "alias/aws/sqs"

  tags = {
    Pipeline = "events"
    Role     = "dlq"
  }
}

# ── Events Queue ──────────────────────────────────────────────────────────────

resource "aws_sqs_queue" "events" {
  name                       = "${local.name_prefix}-events-queue"
  message_retention_seconds  = var.sqs_message_retention_seconds
  visibility_timeout_seconds = var.sqs_visibility_timeout_seconds
  kms_master_key_id          = "alias/aws/sqs"

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.events_dlq.arn
    maxReceiveCount     = var.dlq_max_receive_count
  })

  tags = {
    Pipeline = "events"
    Role     = "main"
  }
}

# ── Social DLQ ────────────────────────────────────────────────────────────────

resource "aws_sqs_queue" "social_dlq" {
  name                       = "${local.name_prefix}-social-dlq"
  message_retention_seconds  = 1209600
  visibility_timeout_seconds = 30
  kms_master_key_id          = "alias/aws/sqs"

  tags = {
    Pipeline = "social"
    Role     = "dlq"
  }
}

# ── Social Queue ──────────────────────────────────────────────────────────────

resource "aws_sqs_queue" "social" {
  name                       = "${local.name_prefix}-social-queue"
  message_retention_seconds  = var.sqs_message_retention_seconds
  visibility_timeout_seconds = var.sqs_visibility_timeout_seconds
  kms_master_key_id          = "alias/aws/sqs"

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.social_dlq.arn
    maxReceiveCount     = var.dlq_max_receive_count
  })

  tags = {
    Pipeline = "social"
    Role     = "main"
  }
}

# ── Queue policies — allow scraper Lambda to send messages ────────────────────

data "aws_iam_policy_document" "events_queue_policy" {
  statement {
    effect    = "Allow"
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.events.arn]
    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.events_scraper.arn]
    }
  }
}

resource "aws_sqs_queue_policy" "events" {
  queue_url = aws_sqs_queue.events.id
  policy    = data.aws_iam_policy_document.events_queue_policy.json
}

data "aws_iam_policy_document" "social_queue_policy" {
  statement {
    effect    = "Allow"
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.social.arn]
    principals {
      type        = "AWS"
      identifiers = [aws_iam_role.events_scraper.arn]
    }
  }
}

resource "aws_sqs_queue_policy" "social" {
  queue_url = aws_sqs_queue.social.id
  policy    = data.aws_iam_policy_document.social_queue_policy.json
}
