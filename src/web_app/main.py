from __future__ import annotations

from fastapi import FastAPI

from web_app.routes import router
from env import env  # noqa

app = FastAPI()

app.include_router(router)
