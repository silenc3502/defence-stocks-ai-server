from sqlalchemy.orm import Session

from app.domains.post.adapter.outbound.persistence.post_repository import PostRepository
from app.domains.post.domain.entity.post import Post
from app.domains.post.infrastructure.mapper.post_mapper import PostMapper


class PostRepositoryImpl(PostRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, post: Post) -> Post:
        orm = PostMapper.to_orm(post)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return PostMapper.to_entity(orm)
