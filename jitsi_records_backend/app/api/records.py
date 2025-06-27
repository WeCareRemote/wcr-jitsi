from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import check_greyt_auth_token
from app.crud.jitsi_record import CRUDJitsiRecord, MultiResult
from app.schemas import Pagination

router = APIRouter()


@router.get("/", summary="List records", response_model=MultiResult)
async def handle_new_records(user: dict = Depends(check_greyt_auth_token),
                             pagination: Pagination = Depends(),
                             db: Session = Depends(get_db)):
    return CRUDJitsiRecord.get_multi(db=db, **pagination.dict(), user_id=user['id'])
