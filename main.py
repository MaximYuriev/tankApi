from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import  FastAPI
import uvicorn

from routers.auth import auth_router
from routers.game import game_router
from pages.router import page_router


from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from redis import asyncio as aioredis

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(game_router)
app.include_router(page_router)


if __name__ == '__main__':
    uvicorn.run("main:app",reload=True)