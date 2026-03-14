from app.domains.auth.domain.entity.member import Member
from app.domains.auth.infrastructure.orm.member_orm import MemberORM


class MemberMapper:
    @staticmethod
    def to_orm(member: Member) -> MemberORM:
        return MemberORM(
            kakao_id=member.kakao_id,
            name=member.name,
            email=member.email,
            created_at=member.created_at,
        )

    @staticmethod
    def to_entity(orm: MemberORM) -> Member:
        return Member(
            member_id=orm.id,
            kakao_id=orm.kakao_id,
            name=orm.name,
            email=orm.email,
            created_at=orm.created_at,
        )
