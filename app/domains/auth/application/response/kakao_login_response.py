from pydantic import BaseModel


class KakaoLoginResponse(BaseModel):
    access_token: str
