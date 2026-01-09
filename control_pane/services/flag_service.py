from typing import Any
from fastapi import Depends, HTTPException
from ..database.connection import get_db_conn
from ..schemas import Flag
from ..utils.oauth2 import get_current_user
from ..utils.rls import get_rls_db

import uuid


async def create_flag(flag:Flag,current_user = Depends(get_current_user), db = Depends(get_rls_db)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403,detail="User doesn't have enough permissions to perform this action")
    
    data = flag.model_dump()    

    query = """
            INSERT INTO flags (tenant_id,key,description,enabled,rollout_percent,variant_weights,rules,created_by) VALUES ($1,$2,$3,$4,$5,$6,$7,$8) RETURNING *
            """

    created_flag = await db.fetchrow(query,current_user['tenant_id'],data['key'],data['description'],data['enabled'],data['rollout_percent'],str(data['variant_weights']),str(data['rules']),current_user['id'])
    
    return created_flag


async def get_flags(current_user = Depends(get_current_user), db = Depends(get_rls_db)):
    query = """
            SELECT * FROM flags WHERE tenant_id = $1
            """
    flags = await db.fetch(query,current_user['tenant_id'])
    return flags

async def get_flag_by_key(flag_key:str,current_user = Depends(get_current_user), db = Depends(get_rls_db)):
    query = """
            SELECT * FROM flags WHERE tenant_id = $1 AND key = $2
            """
    flag = await db.fetchrow(query,current_user['tenant_id'],flag_key)
    if not flag:
        raise HTTPException(status_code=404,detail="Flag not found")
    return flag

async def update_flag(flag_key:str,flag:Flag,current_user = Depends(get_current_user), db = Depends(get_rls_db)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403,detail="User doesn't have enough permissions to perform this action")
    
    data = flag.model_dump()    

    query = """
            UPDATE flags SET description = $1, enabled = $2, rollout_percent = $3, variant_weights = $4, rules = $5 WHERE tenant_id = $6 AND key = $7 RETURNING *
            """

    updated_flag = await db.fetchrow(query,data['description'],data['enabled'],data['rollout_percent'],str(data['variant_weights']),str(data['rules']),current_user['tenant_id'],flag_key)
    
    if not updated_flag:
        raise HTTPException(status_code=404,detail="Flag not found")
    
    return updated_flag

async def delete_flag(flag_key:str,current_user = Depends(get_current_user), db = Depends(get_rls_db)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403,detail="User doesn't have enough permissions to perform this action")
    
    query = """
            DELETE FROM flags WHERE tenant_id = $1 AND key = $2 RETURNING *
            """

    deleted_flag = await db.fetchrow(query,current_user['tenant_id'],flag_key)
    
    if not deleted_flag:
        raise HTTPException(status_code=404,detail="Flag not found")
    
    return {"detail":"Flag deleted successfully"}
