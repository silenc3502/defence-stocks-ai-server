from datetime import datetime, timedelta

import jwt

from app.infrastructure.config.settings import settings


class JwtProvider:
    def generate_token(self, member_id: int) -> str:
        payload = {
            "sub": str(member_id),
            "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes),
        }
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
