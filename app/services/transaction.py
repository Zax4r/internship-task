from decimal import Decimal

from loguru import logger
from sqlalchemy.exc import NoResultFound

from app.core.enums import (
    CurrencyEnum,
    TransactionStatusEnum,
    UserStatusEnum,
)
from app.core.exceptions import (
    BadRequestDataException,
    CreateTransactionForBlockedUserException,
    NegativeBalanceException,
    TransactionAlreadyRollbackedException,
    TransactionDoesNotBelongToUserException,
    TransactionNotExistsException,
    UpdateTransactionForBlockedUserException,
    UserBalanceDoesNotExistException,
    UserNotExistsException,
)
from app.models.transaction import Transaction
from app.models.user import User
from app.repositories.transaction.base import BaseTransactionRepository
from app.repositories.uow.base import BaseUnitOfWork
from app.repositories.user.base import BaseUserRepository
from app.schemas.transaction import RequestTransactionModel, TransactionModel


class TransactionService:
    def __init__(
        self,
        uow: BaseUnitOfWork,
        user_repo: BaseUserRepository,
        transaction_repo: BaseTransactionRepository,
    ):
        self.uow = uow
        self.user_repo = user_repo
        self.transaction_repo = transaction_repo

    async def get_transactions(self, user_id: int | None = None) -> list[TransactionModel]:
        async with self.uow:
            transactions = await self.transaction_repo.get_transactions(user_id=user_id)

        results = []
        for t in transactions:
            result = TransactionModel.model_validate(t)
            results.append(result)
        return results

    async def add_transaction(self, user_id: int, transaction: RequestTransactionModel) -> TransactionModel:
        if user_id < 0:
            raise BadRequestDataException(detail='Unprocessable data in request')
        if transaction.currency not in {str(x) for x in CurrencyEnum}:
            raise BadRequestDataException(detail='Currency does not exist')
        if transaction.amount == 0:
            raise BadRequestDataException(detail='Transaction can not have zero amount')

        logger.info(f'Adding transaction with user_id=`{user_id}`')
        async with self.uow:
            try:
                db_user = await self.user_repo.get_user_by_id(user_id)
            except NoResultFound as exc:
                raise UserNotExistsException(detail=f'User with id=`{user_id}` does not exist') from exc

            if db_user.status != UserStatusEnum.ACTIVE:
                raise CreateTransactionForBlockedUserException(detail=f'User with id=`{user_id}` is blocked')

            try:
                db_user_balance = await self.user_repo.get_user_balance(user_id=user_id, currency=transaction.currency)
            except NoResultFound as exc:
                raise UserBalanceDoesNotExistException(
                    detail=f'User balance user_id=`{user_id}` with currency=`{transaction.currency}` doesn`t exists'
                ) from exc

            new_amount = Decimal(db_user_balance.amount) + transaction.amount
            if new_amount < 0:
                raise NegativeBalanceException(detail='Negative balance')

            await self.user_repo.update_user_balance(balance_id=db_user_balance.id, new_amount=new_amount)
            new_transaction = await self.transaction_repo.add_transaction(
                user_id, transaction.currency, transaction.amount
            )
        logger.info(f'Transaction with user_id=`{user_id}` added')

        result = TransactionModel.model_validate(new_transaction)
        return result

    async def patch_rollback_transaction(self, user_id: int, transaction_id: int) -> TransactionModel:
        if user_id < 0 or transaction_id < 0:
            raise BadRequestDataException(detail='Unprocessable data in request')

        logger.info(f'Updating transaction with user_id=`{user_id}`')
        async with self.uow:
            try:
                db_user = await self.user_repo.get_user_by_id(user_id)
            except NoResultFound as exc:
                raise UserNotExistsException(detail=f'User with id=`{user_id}` does not exist') from exc

            try:
                db_transaction = await self.transaction_repo.get_transaction_by_id(transaction_id)
            except NoResultFound as exc:
                raise TransactionNotExistsException(
                    detail=f'Transaction with id=`{transaction_id}` does not exist'
                ) from exc

            self._validate_transaction(db_transaction=db_transaction, db_user=db_user)

            try:
                db_user_balance = await self.user_repo.get_user_balance(
                    user_id=user_id, currency=db_transaction.currency
                )
            except NoResultFound as exc:
                raise UserBalanceDoesNotExistException(
                    detail=f'User balance user_id=`{user_id}` with currency=`{db_transaction.currency}` doesn`t exists'
                ) from exc

            new_amount = Decimal(db_user_balance.amount) - Decimal(db_transaction.amount)

            if new_amount < 0:
                raise NegativeBalanceException(detail=f'Negative balance: {new_amount}')

            await self.user_repo.update_user_balance(balance_id=db_user_balance.id, new_amount=new_amount)
            await self.transaction_repo.update_transaction(
                transaction_id=db_transaction.id, new_status=TransactionStatusEnum.ROLLBACKED.value
            )
            new_db_transaction = await self.transaction_repo.get_transaction_by_id(transaction_id=db_transaction.id)
        logger.info(f'Transaction with user_id=`{user_id}` updated')

        result = TransactionModel.model_validate(new_db_transaction)
        return result

    def _validate_transaction(self, db_transaction: Transaction, db_user: User) -> None:
        if db_transaction.user_id != db_user.id:
            raise TransactionDoesNotBelongToUserException(
                detail=f'Transaction with id=`{db_transaction.id}` does not belong to user with id=`{db_user.id}`'
            )
        if db_transaction.status == TransactionStatusEnum.ROLLBACKED:
            raise TransactionAlreadyRollbackedException(
                detail=f'Transaction with id=`{db_transaction.id}` is already rollbacked'
            )
        if db_user.status == UserStatusEnum.BLOCKED:
            raise UpdateTransactionForBlockedUserException(detail=f'User with id=`{db_user.id}` is blocked')
