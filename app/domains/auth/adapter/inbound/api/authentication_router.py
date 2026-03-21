from fastapi import APIRouter, Cookie, Depends, HTTPException

from app.domains.auth.application.response.temp_user_info_response import TempUserInfoResponse
from app.domains.auth.application.usecase.get_temp_user_info_usecase import GetTempUserInfoUseCase
from app.domains.auth.dependency import get_get_temp_user_info_usecase

router = APIRouter(prefix="/authentication", tags=["Authentication"])


@router.get("/me", response_model=TempUserInfoResponse)
def get_temp_user_info(
    temp_token: str = Cookie(None),
    usecase: GetTempUserInfoUseCase = Depends(get_get_temp_user_info_usecase),
):
    if not temp_token:
        raise HTTPException(status_code=400, detail="임시 토큰이 누락되었습니다.")

    try:
        return usecase.execute(temp_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
