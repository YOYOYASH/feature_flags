from ..utils.redis_utils import cache
from ..utils.flag_utils import get_flag_hash
from fastapi import Depends, HTTPException
from ..database.connection import db
import asyncio
import logging
from datetime import datetime
import json
from logging_config import setup_logging


setup_logging()

logger = logging.getLogger(__name__)

REFRESH_INTERVAL_SECONDS = 10
ERROR_BACKOFF_SECONDS = 5


async def async_refresher() -> None:
    """
    Periodically refresh flag configurations for all tenants.
    This function is meant to run as a long-lived background task.
    """

    logger.info("async_refresher_starting")

    await db.connect()

    try:
        while True:
            try:
                async with db.pool.acquire() as conn:
                    rows = await conn.fetch(
                        """
                        SELECT
                            t.id AS tenant_id,
                            jsonb_agg(
                                jsonb_build_object(
                                    'flag_key', f.key,
                                    'enabled', f.enabled,
                                    'rollout_percent', f.rollout_percent,
                                    'rules', f.rules,
                                    'variant_weights', f.variant_weights
                                )
                            ) AS flags
                        FROM tenants t
                        JOIN flags f ON f.tenant_id = t.id
                        GROUP BY t.id;
                        """
                    )

                for row in rows:
                    tenant_id = row["tenant_id"]
                    raw_flags = row["flags"] or []

                    try:
                        new_hash, normalized_flags = get_flag_hash(raw_flags)

                        cache_key = f"flags:{tenant_id}"
                        version_key = f"flags:{tenant_id}:version"

                        cached_version = await cache.get(version_key)

                        if cached_version == new_hash:
                            continue

                        updated_data = {
                            "config":normalized_flags,
                            "version":new_hash,
                            "last_refreshed": datetime.now().isoformat()
                        }

                        await cache.set(cache_key, json.dumps(updated_data))
                        await cache.set(version_key, new_hash)

                        logger.info(
                            "tenant_flags_updated",
                            extra={
                                "context": {
                                    "tenant_id": str(tenant_id),
                                    "version": new_hash[:8],
                                }
                            },
                        )

                    except Exception:
                        logger.exception(
                            "tenant_refresh_failed",
                            extra={"context": {"tenant_id": str(tenant_id)}},
                        )

            except asyncio.CancelledError:
                logger.info("async_refresher_cancelled")
                raise  # MUST re-raise

            except Exception:
                logger.exception("async_refresher_iteration_failed")
                await asyncio.sleep(ERROR_BACKOFF_SECONDS)

            await asyncio.sleep(REFRESH_INTERVAL_SECONDS)

    finally:
        logger.info("async_refresher_shutting_down")
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(async_refresher())