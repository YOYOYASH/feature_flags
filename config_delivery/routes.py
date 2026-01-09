from fastapi import APIRouter
from .services.bootstrap_service import bootstrap_service

router = APIRouter()

router.add_api_route('/v1/sdk/bootstrap',endpoint=bootstrap_service,methods=['GET'])