import uuid

from pydantic import BaseModel


class UserGet(BaseModel):
    user_id: str | uuid.UUID
