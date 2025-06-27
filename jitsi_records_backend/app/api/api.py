from fastapi import APIRouter

from app.api import records, records_handler
from app.core.tags import Tags

router = APIRouter(prefix="/api")
router.include_router(records.router, prefix="/records", tags=[Tags.records])
router.include_router(records_handler.router, prefix="/records-handler", tags=[Tags.records_handler])
