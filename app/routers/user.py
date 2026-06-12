from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.core.uow import UnitOfWork
from app.repositories.user import UserRepository
from app.schemas.user import RequestListUserModel, RequestUserModel, RequestUserUpdateModel, ResponseUserModel, UserModel
from app.services.user import UserService

router = APIRouter()


def get_user_service(session: AsyncSession = Depends(get_async_session)) -> UserService:
    uow = UnitOfWork(session=session)
    user_repo = UserRepository(session=session)
    return UserService(uow=uow, user_repo=user_repo)


@router.get('/users', response_model=list[ResponseUserModel], status_code=status.HTTP_200_OK)
async def get_users(
    user_id: int | None = None, email: str | None = None, user_status: str | None = None, service: UserService = Depends(get_user_service)
) -> list[ResponseUserModel]:
    filters = RequestListUserModel(user_id=user_id, email=email, user_status=user_status)
    return await service.get_users(filters)


@router.post('/users', response_model=UserModel, status_code=status.HTTP_200_OK)
async def post_user(user: RequestUserModel, service: UserService = Depends(get_user_service)) -> UserModel:
    return await service.add_user(user)


@router.patch('/users/{user_id}', response_model=UserModel)
async def patch_user(user_id: int, user: RequestUserUpdateModel, service: UserService = Depends(get_user_service)) -> UserModel:
    return await service.update_user(user_id, user)
