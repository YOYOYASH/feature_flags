from fastapi import Depends, HTTPException, Request
from ..database.connection import get_db_conn
from ..utils.service_auth import get_service_auth
from ..utils.rls import get_rls_db
from ..utils.redis_utils import cache
from ..utils.flag_utils import get_flag_hash
import json
from datetime import datetime

async def bootstrap_service(request:Request,db = Depends(get_rls_db), service_principal = Depends(get_service_auth)):
    tenant_id = service_principal['tenant_id']
    client_version = request.query_params.get('curr_version',"")
    cache_key = f"flags:{tenant_id}"
    version_key = f"flags:{tenant_id}:version"

    cached_version = await cache.get(version_key)

    if cached_version == client_version:
        return {
            "changed": False
        }


    cached_flags = await cache.get(cache_key)
    if cached_flags:
        data = json.loads(cached_flags)
        return data

    else:
        query = """
                    SELECT t.id,
                    JSON_ARRAYAGG(
                    JSON_OBJECT(
                                'flag_key':f.key,
                                'enabled':f.enabled,
                                'rollout_percent':f.rollout_percent,
                                'rules':f.rules,
                                'variant_weights':f.variant_weights
                                )
                            ) as flags
                            FROM tenants t JOIN flags f ON t.id = f.tenant_id WHERE t.id = $1 GROUP BY t.id
                                
                            """
        tenant_flag_details = await db.fetchrow(query,tenant_id)
        raw_flags = tenant_flag_details['flags']
        if not tenant_flag_details or not tenant_flag_details["flags"]:
            return {
                "config": {},
                "version": ""
            }

        new_hash,normalized_data = get_flag_hash(raw_flags)

        updated_data = {
            "config":normalized_data,
            "version":new_hash,
            "last_refreshed": datetime.now().isoformat()
        }
        await cache.set(version_key,new_hash)   
        await cache.set(cache_key,json.dumps(updated_data))
        return updated_data


        