from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exception_handlers import http_exception_handler
from loguru import logger

from app.consumers.analytics import get_analytics_consumer
from app.consumers.avro_example import get_avro_consumer
from app.consumers.runner import ConsumerRunner
from app.core.database import create_db_and_tables
from app.core.exceptions import AppException
from app.core.logger import setup_logging
from app.routers.analytics import router as analytics_router
from app.routers.avro_example import router as avro_router
from app.routers.transaction import router as transaction_router
from app.routers.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await create_db_and_tables()
    consumer_runner = ConsumerRunner([get_analytics_consumer(), get_avro_consumer()])
    await consumer_runner.start()
    yield
    await consumer_runner.stop()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(AppException)
async def custom_http_exception_handler(request: Request, exc: HTTPException) -> Response:
    logger.error('Unexpected error: ', exc_info=str(exc))
    return await http_exception_handler(request, exc)


app.include_router(user_router)
app.include_router(transaction_router)
app.include_router(analytics_router)
app.include_router(avro_router)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
