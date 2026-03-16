"""
Supabase client utility — shared across all Lambda services.
Reads credentials from environment variables (local .env) or SSM (production).
"""
from __future__ import annotations

import os
import functools
from supabase import create_client, Client


@functools.lru_cache(maxsize=1)
def get_client() -> Client:
    """Return a cached Supabase client. Safe to call on every request."""
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_KEY"]
    return create_client(url, key)
