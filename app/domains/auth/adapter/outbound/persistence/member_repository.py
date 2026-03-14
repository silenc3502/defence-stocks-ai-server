from abc import ABC, abstractmethod
from typing import Optional

from app.domains.auth.domain.entity.member import Member


class MemberRepository(ABC):
    @abstractmethod
    def find_by_kakao_id(self, kakao_id: str) -> Optional[Member]:
        pass

    @abstractmethod
    def save(self, member: Member) -> Member:
        pass
