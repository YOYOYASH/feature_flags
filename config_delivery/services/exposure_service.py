import json
from fastapi import Depends, HTTPException, Request
from  ..utils.service_auth import get_service_auth
from  ..utils.rls import get_rls_db
from ..utils.redis_utils import cache
from  ..schemas import ExposurePayload
from ..database.connection import db
import logging
import asyncio
from datetime import datetime


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
            await redis_client.xadd(f"stream:events",
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
            continue
        
    return 202


async def run_worker():
    try:
        await db.connect()
        while True:
            try:
                responses = await redis_client.xreadgroup(
                    groupname="events_group",
                    consumername="worker-1",
                    streams= {"stream:events":">"},
                    count = 100,
                    block=5000
                )

                if not responses:
                    continue
                    
                message_ids = []
                records = []
                print(responses)
                for stream,messages in responses:
                    for message_id,value in messages:
                        try:
                            parsed_data = parse_data(value)
                        except KeyError:
                            continue
                        message_ids.append(message_id)
                        records.append(parsed_data)
                print(message_ids)

                if not records:
                    continue
                
                async with db.pool.acquire() as conn:
                    async with conn.transaction():
                        await conn.copy_records_to_table(
                                                        "exposures",
                                                        records=records,
                                                        columns=[
                                                            "tenant_id",
                                                            "flag_key",
                                                            "user_id",
                                                            "context",
                                                            "created_at",
                                                        ],
                                                        )
                if message_ids:
                    await redis_client.xack(
                        "stream:events",
                        "events_group",
                        *message_ids
                    )    
                    
                print(f"Inserted and acked {len(records)}")
            except asyncio.CancelledError:
                raise
            except Exception as e:
                print("Execption occured during ingestion : ",str(e))
                continue
    finally:
        await db.disconnect()

def parse_data(data: dict):
    return (
        data["tenant_id"],
        data["flag_key"],
        data["user_id"],
        data["context"],
        datetime.fromisoformat(data["timestamp"])
    )



print(__name__)

if __name__ =="__main__":
    try:
        asyncio.run(run_worker())
    except asyncio.exceptions.CancelledError:
            raise
    except KeyboardInterrupt:
        raise