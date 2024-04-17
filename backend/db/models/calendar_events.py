# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, Text, CheckConstraint
from pydantic import BaseModel, constr
from db.base_class import Base


class SimpleProductSchema(BaseModel):
    cultivator: str
    strain: str
    signed_url: str
    product_type: str

class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    summary = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(
        Text,
        CheckConstraint(
            "length(start_date) < 15", name="calendar_events_start_date_check"
        ),
        nullable=False,
    )
    end_date = Column(
        Text,
        CheckConstraint("length(end_date) < 15", name="calendar_events_end_date_check"),
        nullable=False,
    )

    def __repr__(self):
        return f"<CalendarEvent(event_id={self.event_id}, summary={self.summary}, description={self.description}, start_date={self.start_date}, end_date={self.end_date})>"


class CalendarEventQuery(BaseModel):
    summary: str
    description: str | None = None
    start_date: constr(max_length=14)
    end_date: constr(max_length=14)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "summary": "Cult Event Title",
                "description": "Cannabis Cult event description.",
                "start_date": "DD/MM/YYYY",
                "end_date": "DD/MM/YYYY"
            }
        }