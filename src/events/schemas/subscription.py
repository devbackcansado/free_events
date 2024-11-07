from pydantic import BaseModel
from uuid import UUID


class SubscriptionCreate(BaseModel):
    event_uid: UUID
