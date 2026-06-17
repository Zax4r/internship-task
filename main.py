import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exception_handlers import http_exception_handler
from loguru import logger

from app.consumers.analytics import get_analytics_consumer
from app.core.database import create_db_and_tables
from app.core.exceptions import AppException
from app.core.logger import setup_logging
from app.routers.analytics import router as analytics_router
from app.routers.transaction import router as transaction_router
from app.routers.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await create_db_and_tables()
    analytics_consumer = await get_analytics_consumer()
    task = asyncio.create_task(analytics_consumer.start())
    yield
    task.cancel()
    await analytics_consumer.stop()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(AppException)
async def custom_http_exception_handler(request: Request, exc: HTTPException) -> Response:
    logger.error(f'Unexpected error: {exc}', exc_info=True)
    return await http_exception_handler(request, exc)


app.include_router(user_router)
app.include_router(transaction_router)
app.include_router(analytics_router)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
