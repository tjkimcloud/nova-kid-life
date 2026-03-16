"""
SQS publisher — sends scraped events/deals to the enrichment queue in batches.
"""
from __future__ import annotations

import json
import logging
import os
from itertools import islice

import boto3

from .models import RawEvent

logger = logging.getLogger(__name__)

_sqs = None


def _get_sqs():
    global _sqs
    if _sqs is None:
        _sqs = boto3.client("sqs", region_name=os.getenv("AWS_REGION", "us-east-1"))
    return _sqs


def _chunks(iterable, size: int):
    it = iter(iterable)
    while chunk := list(islice(it, size)):
        yield chunk


def publish(events: list[RawEvent], queue_url: str) -> int:
    """
    Publish events to SQS in batches of 10 (SQS max per send_message_batch).
    Returns the total number of successfully published messages.
    """
    if not events:
        return 0

    sqs = _get_sqs()
    published = 0
    failed = 0

    for batch in _chunks(events, 10):
        entries = [
            {
                "Id": str(i),
                "MessageBody": json.dumps(event.to_dict()),
                # Group by source so related events are processed together
                "MessageGroupId": batch[i].source_name
                if queue_url.endswith(".fifo")
                else None,
            }
            for i, event in enumerate(batch)
        ]
        # Remove None MessageGroupId for standard queues
        entries = [{k: v for k, v in e.items() if v is not None} for e in entries]

        try:
            resp = sqs.send_message_batch(QueueUrl=queue_url, Entries=entries)
            batch_ok = len(resp.get("Successful", []))
            batch_fail = len(resp.get("Failed", []))
            published += batch_ok
            failed += batch_fail

            if batch_fail:
                for failure in resp.get("Failed", []):
                    logger.error(
                        "SQS publish failed for entry %s: %s — %s",
                        failure["Id"],
                        failure["Code"],
                        failure["Message"],
                    )
        except Exception as exc:
            logger.exception("SQS batch send error: %s", exc)
            failed += len(batch)

    logger.info("Published %d events to SQS (%d failed)", published, failed)
    return published
