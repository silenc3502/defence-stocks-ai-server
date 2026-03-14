from abc import ABC, abstractmethod

from app.domains.post.domain.entity.post import Post


class PostRepository(ABC):
    @abstractmethod
    def save(self, post: Post) -> Post:
        pass
