"""
Scheduler Lambda — EventBridge trigger stub.

EventBridge currently targets the events-scraper Lambda directly.
This function is reserved for future orchestration needs such as:
  - Multi-step fan-out (scrape → enrich → notify)
  - Rate-controlled invocation
  - Cross-service coordination

To activate: update eventbridge.tf target to point here,
then add orchestration logic below.
"""
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    logger.info("Scheduler triggered", extra={"event": json.dumps(event)})
    return {"statusCode": 200, "body": "scheduler stub — no action taken"}
