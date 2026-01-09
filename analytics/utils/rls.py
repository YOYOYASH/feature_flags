from fastapi import Depends, HTTPException
from ..database.connection import get_db_conn
from .service_auth import get_service_auth

async def get_rls_db(service_prnicipal = Depends(get_service_auth),db = Depends(get_db_conn)):
    tenant_id = service_prnicipal['tenant_id']
    if not tenant_id:
        raise HTTPException(status_code=403, detail="User has no tenant assigned")
    
    await db.execute(f"SET LOCAL app.tenant_id = '{tenant_id}'")

    yield db