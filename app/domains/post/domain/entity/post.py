from datetime import datetime
from typing import Optional


class Post:
    def __init__(
        self,
        title: str,
        content: str,
        post_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
    ):
        self.post_id = post_id
        self.title = title
        self.content = content
        self.created_at = created_at or datetime.now()

    def validate(self) -> None:
        if not self.title or not self.title.strip():
            raise ValueError("게시물 제목은 비어 있을 수 없습니다.")
        if not self.content or not self.content.strip():
            raise ValueError("게시물 내용은 비어 있을 수 없습니다.")
