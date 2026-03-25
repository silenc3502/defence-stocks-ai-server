from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.domains.account.adapter.inbound.api.account_router import router as account_router
from app.domains.auth.adapter.inbound.api.auth_router import router as auth_router
from app.domains.auth.adapter.inbound.api.authentication_router import router as authentication_router
from app.domains.auth.adapter.inbound.api.kakao_authentication_router import router as kakao_authentication_router
from app.domains.account.infrastructure.orm.account_orm import AccountORM  # noqa: F401
from app.domains.board.adapter.inbound.api.board_router import router as board_router
from app.domains.board.infrastructure.orm.board_orm import BoardORM  # noqa: F401
from app.domains.market_video.adapter.inbound.api.market_video_router import router as market_video_router
from app.domains.post.adapter.inbound.api.post_router import router as post_router
from app.domains.youtube.adapter.inbound.api.youtube_router import router as youtube_router
from app.domains.post.infrastructure.orm.post_orm import PostORM  # noqa: F401
from app.infrastructure.config.settings import settings
from app.infrastructure.database.session import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_allowed_frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post_router)
app.include_router(board_router)
app.include_router(account_router)
app.include_router(auth_router)
app.include_router(authentication_router)
app.include_router(kakao_authentication_router)
app.include_router(youtube_router)
app.include_router(market_video_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=33333)
