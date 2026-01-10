from fastapi import Depends, HTTPException, Request
from ..utils.service_auth import get_service_auth
from ..utils.rls import get_rls_db
from ..schemas import ExposurePayload
import logging

logger = logging.getLogger(__name__)


async def log_exposure(exposure_data:list[ExposurePayload],db = Depends(get_rls_db),service_principal = Depends(get_service_auth)):
    tenant_id = service_principal['tenant_id']
    try:
        data_to_insert = [(data.model_dump(),tenant_id) for data in exposure_data]

        await db.copy_records_to_table(
            "exposures",
            records = data_to_insert,
            columns = ["tenant_id","flag_key","user_id","context","created_at"]
        )
        return {"inserted":len(exposure_data)}
    except Exception as e:
        logger.exception(f"Error during batch data insertion -> {e}",
                     extra={"context": {"tenant_id": str(tenant_id)}})
