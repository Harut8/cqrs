from app.helpers.db import BaseModel


class User(BaseModel):
    name: str
    email: str
    phone: str



