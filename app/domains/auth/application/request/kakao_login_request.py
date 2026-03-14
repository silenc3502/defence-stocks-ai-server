from pydantic import BaseModel, field_validator


class KakaoLoginRequest(BaseModel):
    authorization_code: str

    @field_validator("authorization_code")
    @classmethod
    def code_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("인가 코드는 비어 있을 수 없습니다.")
        return v
