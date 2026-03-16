"""
SSM Parameter Store helper for social-poster Lambda.
Caches parameters in memory for the Lambda container lifetime.
"""
import os
import logging

logger = logging.getLogger(__name__)

_cache: dict[str, str] = {}


def get_ssm_parameter(name: str) -> str:
    """Fetch a parameter from SSM (with in-process cache).

    Falls back to environment variables for local development.
    """
    if name in _cache:
        return _cache[name]

    # Local dev: map SSM paths to env var names
    env_map = {
        "/novakidlife/ayrshare/api-key":     "AYRSHARE_API_KEY",
        "/novakidlife/supabase/url":         "SUPABASE_URL",
        "/novakidlife/supabase/service-key": "SUPABASE_SERVICE_KEY",
    }
    env_key = env_map.get(name, name.split("/")[-1].upper().replace("-", "_"))
    env_val  = os.environ.get(env_key)
    if env_val:
        _cache[name] = env_val
        return env_val

    # Production: fetch from AWS SSM
    try:
        import boto3
        ssm    = boto3.client("ssm", region_name=os.environ.get("AWS_REGION", "us-east-1"))
        result = ssm.get_parameter(Name=name, WithDecryption=True)
        value  = result["Parameter"]["Value"]
        _cache[name] = value
        return value
    except Exception as exc:
        raise RuntimeError(f"Could not load SSM parameter '{name}': {exc}") from exc
