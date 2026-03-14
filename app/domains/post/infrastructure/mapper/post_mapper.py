from app.domains.post.domain.entity.post import Post
from app.domains.post.infrastructure.orm.post_orm import PostORM


class PostMapper:
    @staticmethod
    def to_orm(post: Post) -> PostORM:
        return PostORM(
            title=post.title,
            content=post.content,
            created_at=post.created_at,
        )

    @staticmethod
    def to_entity(orm: PostORM) -> Post:
        return Post(
            post_id=orm.id,
            title=orm.title,
            content=orm.content,
            created_at=orm.created_at,
        )
