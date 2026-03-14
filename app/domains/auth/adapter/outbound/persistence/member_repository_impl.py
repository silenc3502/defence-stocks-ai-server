from typing import Optional

from sqlalchemy.orm import Session

from app.domains.auth.adapter.outbound.persistence.member_repository import MemberRepository
from app.domains.auth.domain.entity.member import Member
from app.domains.auth.infrastructure.mapper.member_mapper import MemberMapper
from app.domains.auth.infrastructure.orm.member_orm import MemberORM


class MemberRepositoryImpl(MemberRepository):
    def __init__(self, db: Session):
        self.db = db

    def find_by_kakao_id(self, kakao_id: str) -> Optional[Member]:
        orm = self.db.query(MemberORM).filter(MemberORM.kakao_id == kakao_id).first()
        if orm is None:
            return None
        return MemberMapper.to_entity(orm)

    def save(self, member: Member) -> Member:
        orm = MemberMapper.to_orm(member)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return MemberMapper.to_entity(orm)
