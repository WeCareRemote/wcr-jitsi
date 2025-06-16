import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Enum, DateTime

from app.db.base_class import Base


class DeleteReasonEnum(str, enum.Enum):
    expired = 'expired'


class JitsiRecord(Base):
    __tablename__ = 'jitsi_records'

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, nullable=False)
    advisor_id = Column(Integer, nullable=False)
    student_id = Column(Integer, nullable=False)
    start_time = Column(DateTime())
    url =  Column(String(2083))
    creation_date = Column(DateTime(), default=datetime.utcnow)
    delete_reason = Column(Enum(DeleteReasonEnum), nullable=True)
