from pydantic import BaseModel, model_validator, ConfigDict
from typing import Optional
from datetime import datetime


class EventCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str
    description: str
    start_at: datetime
    address: str

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_at < datetime.now():
            raise ValueError("Data de início não pode ser uma data passada")

        return self


class EventUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: Optional[str] = None
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_at and self.start_at < datetime.now():
            raise ValueError("Data de início não pode ser uma data passada")
        return self
