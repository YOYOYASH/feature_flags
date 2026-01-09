from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4
from datetime import datetime


class Tenant(BaseModel):
    name:str
    plan:Optional[str] = None
    owner_email: EmailStr
    owner_name:str
    secrets:Optional[dict]= {}


class DisplayTenant(BaseModel):
    id:UUID4
    name:str
    plan:Optional[str] = None
    created_at: datetime
    api_key:str
    admin_email:str
    admin_password:str

    class Config:
        from_attributes = True


class Principal(BaseModel):
    tenant_id:UUID4
    type:str
    email:Optional[EmailStr] = None
    name:str
    password:Optional[str] = None
    api_key:Optional[str] = None
    role:str

class DisplayPrincipal(BaseModel):
    id:UUID4
    tenant_id:UUID4
    type:str
    email:Optional[EmailStr] = None
    name:str
    role:str
    created_at:datetime
    api_key:Optional[str] = None

    class Config:
        from_attributes = True

class Flag(BaseModel):
    key:str
    description:Optional[str] = None
    enabled: Optional[bool]  = False
    rollout_percent : Optional[int] = 0
    variant_weights:Optional[dict] = {}
    rules: Optional[dict] = {}

class DisplayFlag(BaseModel):
    id:UUID4
    key:str
    description:Optional[str] = None
    enabled: Optional[bool]  = False
    rollout_percent : Optional[int] = 0
    variant_weights:Optional[dict] = {}
    rules: Optional[dict] = {}
    created_by:Optional[UUID4] = None
    created_at:datetime
    updated_at:datetime

    