from pydantic import BaseModel
from datetime import datetime



class ExposurePayload(BaseModel):
    flag_key:str
    user_id:str
    variant:str
    context:dict
    created_at:datetime
