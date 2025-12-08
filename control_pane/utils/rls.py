from fastapi import Depends, HTTPException
from .oauth2 import get_current_user
from ..database.connection import get_db_conn


async def get_rls_db(user = Depends(get_current_user),db = Depends(get_db_conn)):
    tenant_id = user['tenant_id']
    if not tenant_id:
        raise HTTPException(status_code=403, detail="User has no tenant assigned")
    
    await db.execute('SET LOCAL app.tenant_id = $1',tenant_id)

    yield db