from pydantic import BaseModel


class UserRead(BaseModel):
    name: str
    email: str
    phone: str
    created_at: str
