from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.core.database import create_db_and_tables
from app.routers.transaction import router as transaction_router
from app.routers.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(transaction_router)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
