from loguru import logger
from sqlalchemy.exc import NoResultFound

from app.core.enums import CurrencyEnum, UserStatusEnum
from app.core.exceptions import (
    BadRequestDataException,
    UserAlreadyActiveException,
    UserAlreadyBlockedException,
    UserAlreadyExistsException,
    UserNotExistsException,
)
from app.core.uow import UnitOfWork
from app.repositories.user import UserRepository
from app.schemas.user import (
    RequestListUserModel,
    RequestUserModel,
    RequestUserUpdateModel,
    ResponseUserBalanceModel,
    ResponseUserModel,
    UserModel,
)


class UserService:
    def __init__(self, uow: UnitOfWork, user_repo: UserRepository):
        self.uow = uow
        self.user_repo = user_repo

    async def get_users(self, filters: RequestListUserModel) -> list[ResponseUserModel]:
        async with self.uow:
            users = await self.user_repo.get_users(
                user_id=filters.user_id,
                email=filters.email,
                user_status=filters.user_status,
            )

        results = []
        for user in users:
            user_balances = user.user_balance
            balances = [
                ResponseUserBalanceModel(currency=CurrencyEnum(b.currency), amount=b.amount) for b in user_balances
            ]
            balances_sorted = sorted(balances, key=lambda x: x.amount)  # type: ignore[arg-type, return-value]
            result = ResponseUserModel(
                id=user.id,
                email=user.email,
                status=UserStatusEnum(user.status),
                created=user.created,
                balances=balances_sorted,
            )
            results.append(result)

        return results

    async def add_user(self, user: RequestUserModel) -> UserModel:
        logger.info(f'Adding user with email=`{user.email}`')
        async with self.uow:
            db_user = await self.user_repo.get_user_by_email(email=user.email)
            if db_user:
                raise UserAlreadyExistsException(detail=f'User with email=`{user.email}` already exists')

            currencies = [str(x) for x in CurrencyEnum]
            db_user = await self.user_repo.add_user(email=user.email)
            for currency in currencies:
                await self.user_repo.add_user_balance(user_id=db_user.id, currency=currency)
        logger.info(f'User with email=`{user.email}` added')

        result = UserModel.model_validate(db_user)
        return result

    async def update_user(self, user_id: int, user: RequestUserUpdateModel) -> UserModel:
        logger.info(f'Updating user with id=`{user_id}`')
        async with self.uow:
            if user_id < 0:
                raise BadRequestDataException(detail='Unprocessable data in request')

            try:
                db_user = await self.user_repo.get_user_by_id(user_id=user_id)
            except NoResultFound as exc:
                raise UserNotExistsException(detail=f'User with id=`{user_id}` does not exist') from exc

            if db_user.status == UserStatusEnum.BLOCKED and user.status == UserStatusEnum.BLOCKED:
                raise UserAlreadyBlockedException(detail=f'User with id=`{user_id}` is already blocked')
            if db_user.status == UserStatusEnum.ACTIVE and user.status == UserStatusEnum.ACTIVE:
                raise UserAlreadyActiveException(detail=f'User with id=`{user_id}` is already active')

            await self.user_repo.update_user(user_id, user.status)
            db_user = await self.user_repo.get_user_by_id(user_id=user_id)
        logger.info(f'User with id=`{user_id}` updated')

        result = UserModel.model_validate(db_user)
        return result
