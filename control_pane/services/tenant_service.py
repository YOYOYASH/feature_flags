from typing import Any
from fastapi import Depends, HTTPException
from ..database.connection import get_db_conn
from ..utils.auth_utils import generate_api_key,hash_api_key,verify_api_key, hash_password
from ..schemas import Tenant,DisplayTenant
import uuid


async def create_tenant(tenant:Tenant,db:Any = Depends(get_db_conn)):
    try:
        api_key:str = generate_api_key()
        hashed_key = hash_api_key(api_key)
        data = tenant.model_dump()
        print(data)
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    query = """
            INSERT INTO tenants (name,plan,api_key_hash,secrets) VALUES ($1,$2,$3,$4) RETURNING *
            """
    

    created_tenant = await db.fetchrow(query,data['name'],data['plan'],hashed_key,str(data['secrets']))
    if not created_tenant:
        raise HTTPException(status_code=500,detail="Tenant creation failed")
    

    
    query =  """
            INSERT INTO principals (tenant_id,type,name,email,password_hash,role) VALUES ($1,$2,$3,$4,$5,$6) RETURNING *
            """
    initial_admin_password = str(uuid.uuid4())
    hashed_password = hash_password(initial_admin_password)
    await db.execute(query,created_tenant['id'],'user',data['owner_name'],data['owner_email'],hashed_password,'admin')
            
    return DisplayTenant(id=created_tenant['id'],
                         name=created_tenant['name'],
                         plan=created_tenant['plan'],
                         created_at=created_tenant['created_at'],
                         api_key=api_key,
                         admin_email=data['owner_email'],
                         admin_password=initial_admin_password)