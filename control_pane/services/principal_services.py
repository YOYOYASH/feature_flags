from typing import Any, Optional, Union
from fastapi import Depends, HTTPException
from ..database.connection import get_db_conn
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from ..utils.auth_utils import verify_password, hash_password, generate_api_key, hash_api_key
from ..utils.oauth2 import create_access_token,get_current_user
from ..schemas import Principal, DisplayPrincipal

async def login_principal(user_creds: Annotated[OAuth2PasswordRequestForm,Depends()],db = Depends(get_db_conn)):
    loggedInUser = await db.fetchrow("SELECT name,password_hash  FROM principals WHERE name = $1",user_creds.username,)
    if not loggedInUser:
        raise HTTPException(status_code=404,detail="User not found. Please onboard a principal and try again")

    if not verify_password(loggedInUser['password_hash'],user_creds.password):
        raise HTTPException(status_code=401,detail="Incorrect credentails")
    
    token_data = {
        "sub":user_creds.username
    }

    access_token = create_access_token(token_data)

    return {
        "token" : access_token,
        "type" : "bearer"
    }


async def create_principal(principal:Principal, current_user =  Depends(get_current_user),db = Depends(get_db_conn)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403,detail="User doesn't have enough permissions to perform this action")
    
    data = principal.model_dump()
    print(data)
    created_principal  = {}

    if data['type'] == 'service':
        api_key_hash = hash_api_key(generate_api_key())
        query = """
                INSERT INTO principals  (tenant_id,type,email,name,api_key_hash,role) VALUES ($1,$2,$3,$4,$5,$6) RETURNING *
                """
        
        created_principal = await db.fetchrow(query,data['tenant_id'],data['type'],data['email'],data['name'],api_key_hash,data['role'])

    if data['type'] == 'user' :
        sample_hashed_password = hash_password('Sample@123')

        query = """
                INSERT INTO principals  (tenant_id,type,email,name,password_hash,role) VALUES ($1,$2,$3,$4,$5,$6) RETURNING *
                """
        
        created_principal = await db.fetchrow(query,data['tenant_id'],data['type'],data['email'],data['name'],sample_hashed_password,data['role'])

    return DisplayPrincipal(**created_principal)