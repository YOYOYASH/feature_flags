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

    
