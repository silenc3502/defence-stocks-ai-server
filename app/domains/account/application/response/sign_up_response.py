from pydantic import BaseModel


class SignUpResponse(BaseModel):
    nickname: str
    email: str
