from pydantic import BaseModel


class SignUpRequest(BaseModel):
    nickname: str
    email: str
