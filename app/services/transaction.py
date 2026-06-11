from app.core.enums import CurrencyEnum, TransactionStatusEnum, UserStatusEnum
from app.core.exceptions import (
    BadRequestDataException,
    CreateTransactionForBlockedUserException,
    NegativeBalanceException,
    TransactionAlreadyRollbackedException,
    TransactionDoesNotBelongToUserException,
    TransactionNotExistsException,
    UpdateTransactionForBlockedUserException,
    UserNotExistsException,
)
from app.core.uow import UnitOfWork
from app.repositories.transaction import TransactionRepository
from app.repositories.user import UserRepository
from app.schemas.transaction import RequestTransactionModel, TransactionModel


class TransactionService:
    def __init__(self, uow: UnitOfWork, user_repo: UserRepository, transaction_repo: TransactionRepository):
        self.uow = uow
        self.user_repo = user_repo
        self.transaction_repo = transaction_repo

    async def get_transactions(self, user_id: int | None):
        async with self.uow:
            transactions = await self.transaction_repo.get_transactions(user_id=user_id)

        results = []
        for t in transactions:
            result = TransactionModel.model_validate(t)
            results.append(result)
        return results

    async def add_transaction(self, user_id: int, transaction: RequestTransactionModel) -> TransactionModel:
        async with self.uow:
            if user_id < 0:
                raise BadRequestDataException(detail='Unprocessable data in request')
            if transaction.currency not in {str(x) for x in CurrencyEnum}:
                raise BadRequestDataException(detail='Currency does not exist')
            if transaction.amount == 0:
                raise BadRequestDataException(detail='Transaction can not have zero amount')

            db_user = await self.user_repo.get_user_by_id(user_id)
            if not db_user:
                raise UserNotExistsException(detail=f'User with id=`{user_id}` does not exist')
            if db_user.status != UserStatusEnum.ACTIVE:
                raise CreateTransactionForBlockedUserException(detail=f'User with id=`{user_id}` is blocked')

            db_user_balance = await self.user_repo.get_user_balance(user_id=user_id, currency=transaction.currency)
            new_amount = float(db_user_balance.amount) + transaction.amount
            if new_amount < 0:
                raise NegativeBalanceException(detail='Negative balance')

            await self.user_repo.update_user_balance(balance_id=db_user_balance.id, new_amount=new_amount)
            new_transaction = await self.transaction_repo.add_transaction(user_id, transaction.currency, transaction.amount)

        result = TransactionModel.model_validate(new_transaction)
        return result

    async def patch_rollback_transaction(self, user_id: int, transaction_id: int):
        async with self.uow:
            if user_id < 0 or transaction_id < 0:
                raise BadRequestDataException(detail='Unprocessable data in request')
            db_user = await self.user_repo.get_user_by_id(user_id)
            if not db_user:
                raise UserNotExistsException(detail=f'User with id=`{user_id}` does not exist')

            db_transaction = await self.transaction_repo.get_transaction_by_id(transaction_id)
            if not db_transaction:
                raise TransactionNotExistsException(detail=f'Transaction with id=`{transaction_id}` does not exist')

            if db_transaction.user_id != db_user.id:
                raise TransactionDoesNotBelongToUserException(
                    detail=f'Transaction with id=`{transaction_id}` does not belong to user with id=`{user_id}`'
                )

            if db_transaction.status == TransactionStatusEnum.roll_backed:
                raise TransactionAlreadyRollbackedException(detail=f'Transaction with id=`{transaction_id}` is already rollbacked')
            if db_user.status == UserStatusEnum.BLOCKED:
                raise UpdateTransactionForBlockedUserException(detail=f'User with id=`{user_id}` is blocked')

            db_user_balance = await self.user_repo.get_user_balance(user_id=user_id, currency=db_transaction.currency)
            new_amount = float(db_user_balance.amount) - float(db_transaction.amount)
            if new_amount < 0:
                raise NegativeBalanceException(detail=f'Negative balance: {new_amount}')
            await self.user_repo.update_user_balance(balance_id=db_user_balance.id, new_amount=new_amount)
            await self.transaction_repo.update_transaction(
                transaction_id=db_transaction.id, new_status=TransactionStatusEnum.roll_backed.value
            )
