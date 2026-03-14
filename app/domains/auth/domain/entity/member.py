from datetime import datetime
from typing import Optional


class Member:
    def __init__(
        self,
        kakao_id: str,
        name: str,
        email: str,
        member_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
    ):
        self.member_id = member_id
        self.kakao_id = kakao_id
        self.name = name
        self.email = email
        self.created_at = created_at or datetime.now()
