from fastapi import APIRouter,Depends
from .services.tenant_service import create_tenant
from .services.principal_services import login_principal, create_principal
from .services.flag_service import create_flag, get_flags, get_flag_by_key, update_flag, delete_flag
from .database.connection import get_db_conn
from .schemas import DisplayTenant, DisplayPrincipal, DisplayFlag

router = APIRouter()

router.add_api_route('/v1/tenant',endpoint=create_tenant,methods=['POST'],response_model=DisplayTenant)
router.add_api_route('/v1/login',endpoint=login_principal,methods=['POST'])
router.add_api_route('/v1/principals',endpoint=create_principal,methods=['POST'],response_model=DisplayPrincipal)
router.add_api_route('/v1/flags',endpoint=create_flag,methods=['POST'])
router.add_api_route('/v1/flags',endpoint=get_flags,methods=['GET'])
router.add_api_route('/v1/flags/{flag_key}',endpoint=get_flag_by_key,methods=['GET'])
router.add_api_route('/v1/flags/{flag_key}',endpoint=update_flag,methods=['PUT'])
router.add_api_route('/v1/flags/{flag_key}',endpoint=delete_flag,methods=['DELETE'])