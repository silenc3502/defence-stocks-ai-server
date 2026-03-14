from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class KakaoUserInfo:
    kakao_id: str
    name: str
    email: str


class KakaoAuthPort(ABC):
    @abstractmethod
    def get_kakao_access_token(self, authorization_code: str) -> str:
        pass

    @abstractmethod
    def get_kakao_user_info(self, kakao_access_token: str) -> KakaoUserInfo:
        pass
