from datetime import date

from pydantic import BaseModel


class AnalysisModel(BaseModel):
    start_date: date
    end_date: date
    registered_users_count: int
    registered_and_deposit_users_count: int
    usd_deposits_sum: float
    usd_withdraws_sum: float
    transactions_count: int
    not_rollbacked_transactions_count: int
