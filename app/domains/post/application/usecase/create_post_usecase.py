from app.domains.post.adapter.outbound.persistence.post_repository import PostRepository
from app.domains.post.application.request.create_post_request import CreatePostRequest
from app.domains.post.application.response.create_post_response import CreatePostResponse
from app.domains.post.domain.entity.post import Post


class CreatePostUseCase:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository

    def execute(self, request: CreatePostRequest) -> CreatePostResponse:
        post = Post(title=request.title, content=request.content)
        post.validate()

        saved_post = self.post_repository.save(post)

        return CreatePostResponse(
            post_id=saved_post.post_id,
            title=saved_post.title,
            content=saved_post.content,
            created_at=saved_post.created_at,
        )
