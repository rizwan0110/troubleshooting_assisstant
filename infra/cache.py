import hashlib
import logging
from cachetools import TTLCache

logger = logging.getLogger(__name__)

# Max 100 cached responses, expire after 1 hour
query_cache = TTLCache(maxsize=100, ttl=3600)


def get_cache_key(query: str) -> str:
    normalized = query.strip().lower()
    return hashlib.md5(normalized.encode()).hexdigest()


def get_from_cache(query: str):
    key = get_cache_key(query)
    result = query_cache.get(key)
    if result:
        logger.info(f"Cache HIT for query: '{query[:50]}'")
    else:
        logger.info(f"Cache MISS for query: '{query[:50]}'")
    return result


def save_to_cache(query: str, result: dict):
    key = get_cache_key(query)
    query_cache[key] = result
    logger.info(f"Cached result for query: '{query[:50]}'")
