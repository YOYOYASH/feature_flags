from pydantic import BaseModel, UUID4
from datetime import datetime



class ExposurePayload(BaseModel):
    tenant_id:UUID4
    flag_key:str
    user_id:str
    context:dict
    created_at:datetime
