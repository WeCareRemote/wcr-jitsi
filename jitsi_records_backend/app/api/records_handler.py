from fastapi import APIRouter, Response, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from starlette.status import HTTP_204_NO_CONTENT

from app.background_tasks.records_handler import handle_records
from app.core.config import get_settings, BaseSettings
from app.core.deps import get_db
from app.core.security import verify_bearer_token

router = APIRouter()


@router.post("/", summary="Handle new records",
             status_code=HTTP_204_NO_CONTENT,
             dependencies=[Depends(verify_bearer_token)])
async def handle_new_records(background_tasks: BackgroundTasks,
                             settings: BaseSettings = Depends(get_settings),
                             db: Session = Depends(get_db)):
    background_tasks.add_task(handle_records, db, settings)
    return Response(status_code=HTTP_204_NO_CONTENT)
