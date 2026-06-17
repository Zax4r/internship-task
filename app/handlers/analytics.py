from typing import Any

from loguru import logger

from app.services.analytics import AnalyticsService


class AnalyticsMessageHandler:
    def __init__(self, analytics_service: AnalyticsService):
        self.analytics_service = analytics_service

    async def __call__(self, payload: dict[str, Any]) -> None:
        action = payload.get('action')
        logger.info(f'Handling analytics action: {action}')
        try:
            if action == 'run_analytics':
                data = await self.analytics_service.perform_analysis()
                print('68', data)
            else:
                logger.info(f'Unknown analytics action: {action}')
        except Exception as exc:
            logger.error(exc)
