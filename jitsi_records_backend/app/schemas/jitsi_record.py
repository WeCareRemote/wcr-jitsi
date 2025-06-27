from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models.jitsi_record import DeleteReasonEnum

class JitsiRecordBase(BaseModel):
    conversation_id: int
    advisor_id: int
    student_id: int
    start_time: datetime

class JitsiRecordItem(JitsiRecordBase):
    id: Optional[int]
    url: Optional[str] = Field(None, max_length=2083)
    creation_date: Optional[datetime]
    delete_reason: Optional[DeleteReasonEnum]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "conversation_id": 12,
                "advisor_id": 196,
                "student_id": 10,
                "start_time": "2032-04-23T10:20:30.400Z",
                "url": "https://greyt.me/media/a1b06b9e-a92f-11ec-ba97-95543040d5ea.png",
                "creation_date": "2032-04-23T10:20:30.400Z",
                "delete_reason": None,                                                     
            }
        }
    ) 
                                        
class JitsiRecordCreate(JitsiRecordBase):
    url: str = Field(..., max_length=2083)
                                           
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conversation_id": 12,
                "advisor_id": 196,
                "student_id": 10,
                "start_time": "2032-04-23T10:20:30.400Z",
                "url": "https://greyt.me/media/a1b06b9e-a92f-11ec-ba97-95543040d5ea.png",
            }
        }
    )
