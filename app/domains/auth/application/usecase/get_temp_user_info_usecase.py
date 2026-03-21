from app.domains.auth.adapter.outbound.in_memory.temp_token_repository import TempTokenRepository
from app.domains.auth.application.response.temp_user_info_response import TempUserInfoResponse


class GetTempUserInfoUseCase:
    def __init__(self, temp_token_repository: TempTokenRepository):
        self.temp_token_repository = temp_token_repository

    def execute(self, temp_token: str) -> TempUserInfoResponse:
        print(f"임시 사용자 정보 조회 - temp_token: {temp_token[:8]}...")

        temp_data = self.temp_token_repository.find_by_token(temp_token)
        if temp_data is None:
            print(f"임시 토큰 조회 실패 - temp_token: {temp_token[:8]}...")
            raise ValueError("임시 토큰이 만료되었거나 존재하지 않습니다.")

        print(f"임시 사용자 정보 조회 성공 - nickname: {temp_data['nickname']}, email: {temp_data['email']}")

        return TempUserInfoResponse(
            nickname=temp_data["nickname"],
            email=temp_data["email"],
        )
