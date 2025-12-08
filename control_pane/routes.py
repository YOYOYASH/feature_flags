from fastapi import APIRouter,Depends
from .services.tenant_service import create_tenant
from .services.principal_services import login_principal, create_principal
from .database.connection import get_db_conn
from .schemas import DisplayTenant, DisplayPrincipal

router = APIRouter()

router.add_api_route('/v1/tenant',endpoint=create_tenant,methods=['POST'],response_model=DisplayTenant)
router.add_api_route('/v1/login',endpoint=login_principal,methods=['POST'])
router.add_api_route('/v1/principals',endpoint=create_principal,methods=['POST'],response_model=DisplayPrincipal)