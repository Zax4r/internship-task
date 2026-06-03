import uvicorn
from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import create_db_and_tables, get_async_session
from app.routers.transaction import router as transaction_router
from app.routers.user import router as user_router

app = FastAPI()


@app.on_event('startup')
async def on_startup(session: AsyncSession = Depends(get_async_session)):
    await create_db_and_tables()


app.include_router(user_router)
app.include_router(transaction_router)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
