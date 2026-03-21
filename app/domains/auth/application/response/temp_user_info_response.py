from pydantic import BaseModel


class TempUserInfoResponse(BaseModel):
    is_registered: bool = False
    nickname: str
    email: str
