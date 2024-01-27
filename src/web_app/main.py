from fastapi import FastAPI

from web_app.routes import router
from env import env

app = FastAPI()

app.include_router(router)
