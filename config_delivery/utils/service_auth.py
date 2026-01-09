from fastapi import Request, HTTPException,Depends
import hashlib
from ..database.connection import get_db_conn

async def get_service_auth(request: Request, db = Depends(get_db_conn)):
    service_api_key = request.headers.get("X-API-KEY")
    if not service_api_key:
        raise HTTPException(status_code=401, detail="Service API key missing")

    hashed_key = hash_api_key(service_api_key)


    key_from_db = await db.fetchrow("SELECT api_key_hash FROM principals WHERE api_key_hash = $1", hashed_key)


    if key_from_db is None:
        raise HTTPException(status_code=403, detail="Invalid Service API key")
    
    service_principal = await db.fetchrow("SELECT id, tenant_id, name, type, role,created_at FROM principals WHERE api_key_hash = $1", hashed_key)

    return service_principal


def hash_api_key(api_key:str) -> str:
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return api_key_hash