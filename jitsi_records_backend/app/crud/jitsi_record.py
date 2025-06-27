from typing_extensions import TypedDict
from typing import List
from urllib.parse import urlparse

import boto3
from botocore.client import Config
from fastapi.encoders import jsonable_encoder
from sqlalchemy import asc, desc, or_, case
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.jitsi_record import JitsiRecord
from app.schemas.jitsi_record import JitsiRecordCreate, JitsiRecordItem

MultiResult = TypedDict('MultiResult', {'total_count': int, 'items': List[JitsiRecordItem]})


class CRUDJitsiRecord:
    @staticmethod
    def create(db: Session, *, obj_in: JitsiRecordCreate) -> JitsiRecord:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = JitsiRecord(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def get_multi(
        db: Session, *, user_id: int = None, skip: int = 0, limit: int = 100, order_by: str = None
    ) -> MultiResult:
        items = db.query(JitsiRecord)
        total_count = items.count()
        if user_id:
            items = items.filter(or_(JitsiRecord.advisor_id == user_id, JitsiRecord.student_id == user_id))
        if order_by:
            if order_by.startswith('-'):
                order_direction = desc
                order_by = order_by[1:]
            else:
                order_direction = asc
            items = items.order_by(order_direction(order_by))
        else:
            items = items.order_by(case([(or_(JitsiRecord.url.is_(None), JitsiRecord.url == ""), 1)], else_=0),
                                   desc('start_time'))
        items = items.offset(skip)
        if limit != 0:
            items = items.limit(limit)
        items = [JitsiRecordItem.from_orm(i) for i in items]
        s3_client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                 aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                 region_name='eu-central-1',
                                 config=Config(signature_version='s3v4'))
        for item in items:
            if not item.url:
                continue
            url = urlparse(item.url).path[1:]
            item.url = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': settings.S3_BUCKET, 'Key': url},
                                                        ExpiresIn=settings.PRESIGNED_URL_EXPIRES_IN, HttpMethod='GET')
        return {
            'total_count': total_count,
            'items': items
        }
