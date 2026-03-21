import json
from typing import Optional

import redis

from app.domains.auth.adapter.outbound.in_memory.temp_token_repository import TempTokenRepository

TEMP_TOKEN_TTL_SECONDS = 5 * 60


class TempTokenRepositoryImpl(TempTokenRepository):
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    def _key(self, token: str) -> str:
        return f"temp_token:{token}"

    def save(self, token: str, data: dict) -> None:
        self.redis_client.setex(self._key(token), TEMP_TOKEN_TTL_SECONDS, json.dumps(data))

    def find_by_token(self, token: str) -> Optional[dict]:
        value = self.redis_client.get(self._key(token))
        if value is None:
            return None
        return json.loads(value)

    def delete(self, token: str) -> None:
        self.redis_client.delete(self._key(token))
