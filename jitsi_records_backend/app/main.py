from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import router
from app.core.config import settings
from app.core.http_client import http_client

app = FastAPI(**settings.get_fast_api_init_keys())


@app.on_event("startup")
async def startup():
    http_client.start()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await http_client.stop()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
