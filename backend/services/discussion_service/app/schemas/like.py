from uuid import UUID
from pydantic import BaseModel


class ThreadLikerRead(BaseModel):
    id: UUID
    username: str
    full_name: str
    avatar_url: str | None = None


class ThreadLikersResponse(BaseModel):
    items: list[ThreadLikerRead]
