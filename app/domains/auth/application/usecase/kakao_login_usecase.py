from app.domains.auth.adapter.outbound.external.kakao_auth_port import KakaoAuthPort
from app.domains.auth.adapter.outbound.persistence.member_repository import MemberRepository
from app.domains.auth.application.request.kakao_login_request import KakaoLoginRequest
from app.domains.auth.application.response.kakao_login_response import KakaoLoginResponse
from app.domains.auth.domain.entity.member import Member
from app.infrastructure.security.jwt_provider import JwtProvider


class KakaoLoginUseCase:
    def __init__(
        self,
        member_repository: MemberRepository,
        kakao_auth_port: KakaoAuthPort,
        jwt_provider: JwtProvider,
    ):
        self.member_repository = member_repository
        self.kakao_auth_port = kakao_auth_port
        self.jwt_provider = jwt_provider

    def execute(self, request: KakaoLoginRequest) -> KakaoLoginResponse:
        kakao_access_token = self.kakao_auth_port.get_kakao_access_token(request.authorization_code)
        user_info = self.kakao_auth_port.get_kakao_user_info(kakao_access_token)

        member = self.member_repository.find_by_kakao_id(user_info.kakao_id)
        if member is None:
            member = Member(
                kakao_id=user_info.kakao_id,
                name=user_info.name,
                email=user_info.email,
            )
            member = self.member_repository.save(member)

        access_token = self.jwt_provider.generate_token(member.member_id)
        return KakaoLoginResponse(access_token=access_token)
