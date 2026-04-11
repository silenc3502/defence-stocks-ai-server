import logging
from typing import Any

import httpx
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.infrastructure.config.settings import settings
from app.infrastructure.external.serp.serp_exceptions import (
    SerpAPIRequestError,
    SerpAPIResponseError,
)

logger = logging.getLogger(__name__)

_SEARCH_PATH = "/search.json"
_ACCOUNT_PATH = "/account.json"


class SerpAPIClient:
    """SERP API 공용 HTTP 클라이언트.

    - 인증(api_key) 및 기본 엔진(engine) 을 공통으로 주입한다.
    - 네트워크 오류·타임아웃에 대해 지수 백오프 재시도를 수행한다.
    - HTTP 에러 응답은 명확한 예외로 변환한다.
    - Base URL 은 환경 변수로 교체 가능 (SerpAPI, SearchAPI 등).
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        default_engine: str | None = None,
        timeout_seconds: float | None = None,
        max_retries: int | None = None,
    ):
        self._api_key = api_key or settings.serp_api_key
        self._base_url = (base_url or settings.serp_api_base_url).rstrip("/")
        self._default_engine = default_engine or settings.serp_api_default_engine
        self._timeout_seconds = (
            timeout_seconds
            if timeout_seconds is not None
            else settings.serp_api_timeout_seconds
        )
        self._max_retries = (
            max_retries if max_retries is not None else settings.serp_api_max_retries
        )

        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=self._timeout_seconds,
            headers={"Accept": "application/json"},
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def search(self, query: str, engine: str | None = None, **extra_params: Any) -> dict:
        """SERP API 검색 호출.

        :param query: 검색어 (`q` 파라미터).
        :param engine: 사용할 검색 엔진 (기본값: settings.serp_api_default_engine).
        :param extra_params: 추가 쿼리 파라미터 (예: hl, gl, num 등).
        :return: SERP API JSON 응답.
        """
        params: dict[str, Any] = {
            "engine": engine or self._default_engine,
            "q": query,
            **extra_params,
        }
        return self._request_json(_SEARCH_PATH, params=params)

    def ping(self) -> dict:
        """가용성 스모크 체크. SerpAPI 의 /account.json 엔드포인트를 호출한다."""
        return self._request_json(_ACCOUNT_PATH, params={})

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "SerpAPIClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------
    def _request_json(self, path: str, params: dict[str, Any]) -> dict:
        merged_params = {**params, "api_key": self._api_key}

        try:
            return self._send_with_retry(path, merged_params)
        except RetryError as retry_err:
            last_exc = retry_err.last_attempt.exception()
            logger.error(
                "SERP API 요청 재시도 소진 (path=%s, params=%s): %s",
                path,
                self._redact(params),
                last_exc,
            )
            raise SerpAPIRequestError(
                f"SERP API 요청 실패 ({type(last_exc).__name__}): {last_exc}"
            ) from last_exc

    def _send_with_retry(self, path: str, merged_params: dict[str, Any]) -> dict:
        retryable = (
            httpx.TimeoutException,
            httpx.NetworkError,
            httpx.RemoteProtocolError,
        )

        @retry(
            reraise=True,
            retry=retry_if_exception_type(retryable),
            stop=stop_after_attempt(max(1, self._max_retries)),
            wait=wait_exponential(multiplier=0.5, min=0.5, max=4.0),
        )
        def _do_request() -> dict:
            response = self._client.get(path, params=merged_params)
            return self._handle_response(response, path, merged_params)

        try:
            return _do_request()
        except retryable:  # type: ignore[misc]
            # tenacity(reraise=True) 가 마지막 예외를 그대로 올린다.
            raise

    def _handle_response(
        self,
        response: httpx.Response,
        path: str,
        params: dict[str, Any],
    ) -> dict:
        if response.is_success:
            try:
                return response.json()
            except ValueError as exc:
                logger.error(
                    "SERP API 응답 JSON 파싱 실패 (path=%s): %s", path, exc
                )
                raise SerpAPIResponseError(
                    status_code=response.status_code,
                    message="Invalid JSON response",
                ) from exc

        payload: dict = {}
        try:
            payload = response.json()
        except ValueError:
            payload = {"raw": response.text}

        message = payload.get("error") or response.reason_phrase or "Unknown error"
        logger.error(
            "SERP API 에러 응답 (path=%s, status=%s, params=%s): %s",
            path,
            response.status_code,
            self._redact(params),
            message,
        )
        raise SerpAPIResponseError(
            status_code=response.status_code,
            message=str(message),
            payload=payload,
        )

    @staticmethod
    def _redact(params: dict[str, Any]) -> dict[str, Any]:
        """로그에서 api_key 를 마스킹한다."""
        return {k: ("***" if k == "api_key" else v) for k, v in params.items()}


# 모듈 레벨 싱글톤 — Application / Adapter Layer 에서 공용으로 사용한다.
serp_api_client = SerpAPIClient()
