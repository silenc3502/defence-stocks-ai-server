class SerpAPIError(Exception):
    """SERP API 관련 최상위 예외."""


class SerpAPIRequestError(SerpAPIError):
    """네트워크 오류, 타임아웃 등 SERP API 요청 자체가 실패한 경우."""


class SerpAPIResponseError(SerpAPIError):
    """SERP API 가 에러 상태 코드(4xx/5xx)를 반환한 경우."""

    def __init__(self, status_code: int, message: str, payload: dict | None = None):
        super().__init__(f"[{status_code}] {message}")
        self.status_code = status_code
        self.payload = payload or {}
