from fastapi import HTTPException, status


class AppException(HTTPException):
    default_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Internal server error'

    def __init__(self, status_code: int = None, detail: str = None):
        super().__init__(status_code=status_code or self.default_status_code, detail=detail or self.default_detail)


class BadRequestException(AppException):
    default_status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Bad request'


class NotFoundException(AppException):
    default_status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found'


class ConflictException(AppException):
    default_status_code = status.HTTP_409_CONFLICT
    default_detail = 'Resource already exists'


class UnprocessableException(AppException):
    default_status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Unprocessable data in request'


class UserAlreadyExistsException(ConflictException):
    pass


class UserNotExistsException(NotFoundException):
    pass


class UserAlreadyBlockedException(BadRequestException):
    pass


class UserAlreadyActiveException(BadRequestException):
    pass


class BadRequestDataException(UnprocessableException):
    pass


class NegativeBalanceException(BadRequestException):
    pass


class TransactionNotExistsException(BadRequestException):
    pass


class TransactionDoesNotBelongToUserException(BadRequestException):
    pass


class CreateTransactionForBlockedUserException(NotFoundException):
    pass


class UpdateTransactionForBlockedUserException(BadRequestException):
    pass


class TransactionAlreadyRollbackedException(BadRequestException):
    pass
