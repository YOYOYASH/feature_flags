from fastapi import APIRouter
from .services.exposure_service import log_exposure

router = APIRouter()

router.add_api_route('/v1/sdk/events',endpoint=log_exposure,methods=['POST'])