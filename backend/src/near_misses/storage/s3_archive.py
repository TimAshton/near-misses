import json
from datetime import UTC, datetime
from typing import Any

import boto3

from near_misses.config import settings

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = boto3.client(
            "s3",
            region_name=settings.aws_region,
            endpoint_url=settings.s3_endpoint_url,  # None -> real AWS
        )
    return _client


def archive_raw_response(source: str, raw: dict[str, Any] | list[Any]) -> str:
    """Archive one raw API response for auditing/reprocessing. Returns the S3 key."""
    now = datetime.now(UTC)
    key = f"raw/{source}/{now:%Y/%m/%d}/{now.timestamp():.6f}.json"
    _get_client().put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=json.dumps(raw).encode("utf-8"),
        ContentType="application/json",
    )
    return key
