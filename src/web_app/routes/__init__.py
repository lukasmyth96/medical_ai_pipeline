from fastapi import APIRouter

from web_app.routes.api import pre_authorization_guidelines_ingest_route

router = APIRouter()

router.include_router(pre_authorization_guidelines_ingest_route)
