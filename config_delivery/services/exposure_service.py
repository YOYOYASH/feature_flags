import json
from fastapi import Depends, HTTPException, Request
from  ..utils.service_auth import get_service_auth
from  ..utils.rls import get_rls_db
from ..utils.redis_utils import cache
from  ..schemas import ExposurePayload
import logging

logger = logging.getLogger(__name__)

redis_client = cache.redis

# async def log_exposure(
#     exposure_data: list[ExposurePayload],
#     db = Depends(get_rls_db),
#     service_principal = Depends(get_service_auth),
# ):
#     tenant_id = service_principal["tenant_id"]

#     try:
#         records = []

#         for data in exposure_data:
#             payload = data.model_dump()

#             records.append((
#                 tenant_id,                          # tenant_id
#                 payload["flag_key"],                # flag_key
#                 payload["user_id"],                 # user_id
#                 json.dumps(payload.get("context")), # context (JSONB)
#                 payload["created_at"],              # created_at
#             ))

#         await db.copy_records_to_table(
#             "exposures",
#             records=records,
#             columns=[
#                 "tenant_id",
#                 "flag_key",
#                 "user_id",
#                 "context",
#                 "created_at",
#             ],
#         )

#         return {"inserted": len(records)}

#     except Exception as e:
#         logger.exception(
#             f"Error during batch data insertion -> {e}",
#             extra={"context": {"tenant_id": str(tenant_id)}},
#         )
#         raise

async def log_exposure(
    exposure_data: list[ExposurePayload],
    db = Depends(get_rls_db),
    service_principal = Depends(get_service_auth),
):
    tenant_id = service_principal["tenant_id"]
    
    for event in exposure_data:
        try:
            data = event.model_dump()
            await redis_client.xadd(f"stream:tenant:{tenant_id}:events",
                            fields={
                                "tenant_id": str(tenant_id),
                                "event_type": "exposure",
                                "flag_key":data['flag_key'],
                                "user_id":data["user_id"],
                                "context": json.dumps(data['context']),
                                "timestamp":data["created_at"].isoformat()
                            })
        except Exception as e:
            logger.exception(
            f"Error during batch data ingestion -> {e}",
            extra={"context": {"tenant_id": str(tenant_id)}},
        )
        raise
        
    return 202

