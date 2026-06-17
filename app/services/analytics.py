from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.core.constants import WEEKS_FOR_ANALYTICS
from app.core.enums import EXCHANGE_RATES_TO_USD, CurrencyEnum
from app.core.uow import UnitOfWork
from app.repositories.analytics import AnalyticsRepository
from app.schemas.analytics import AnalysisModel


class AnalyticsService:
    def __init__(self, uow: UnitOfWork, analytics_repo: AnalyticsRepository):
        self.uow = uow
        self.analytics_repo = analytics_repo

    async def perform_analysis(self) -> list[AnalysisModel]:
        results = []
        for i_week in range(1, WEEKS_FOR_ANALYTICS + 1):
            dt_from = datetime.now(timezone.utc).date() - timedelta(weeks=i_week) + timedelta(days=1)
            dt_to = datetime.now(timezone.utc).date() - timedelta(weeks=i_week - 1)

            async with self.uow:
                registered_users_count = await self.analytics_repo.get_registered_users_count(
                    dt_from=dt_from, dt_to=dt_to
                )
                registered_and_deposit_users_count = await self.analytics_repo.get_deposit_users_count(
                    dt_from=dt_from, dt_to=dt_to
                )

                not_rollbacked_deposits = await self.analytics_repo.get_not_rollbacked_deposits(
                    dt_from=dt_from, dt_to=dt_to
                )
                usd_deposits_sum = sum(
                    [
                        x.amount * Decimal(EXCHANGE_RATES_TO_USD[CurrencyEnum(x.currency)])
                        for x in not_rollbacked_deposits
                    ]
                )
                not_rollbacked_withdraws = await self.analytics_repo.get_not_rollbacked_withdraws(
                    dt_from=dt_from, dt_to=dt_to
                )
                usd_withdraws_sum = sum(
                    [
                        x.amount * Decimal(EXCHANGE_RATES_TO_USD[CurrencyEnum(x.currency)])
                        for x in not_rollbacked_withdraws
                    ]
                )

                transactions_count = await self.analytics_repo.get_transactions_count(dt_from=dt_from, dt_to=dt_to)
                not_rollbacked_transactions_count = await self.analytics_repo.get_not_rollbacked_transactions_count(
                    dt_from=dt_from, dt_to=dt_to
                )

            result = AnalysisModel(
                start_date=dt_from,
                end_date=dt_to,
                registered_users_count=registered_users_count,
                registered_and_deposit_users_count=registered_and_deposit_users_count,
                usd_deposits_sum=usd_deposits_sum,
                usd_withdraws_sum=usd_withdraws_sum,
                transactions_count=transactions_count,
                not_rollbacked_transactions_count=not_rollbacked_transactions_count,
            )
            results.append(result)
        return results
