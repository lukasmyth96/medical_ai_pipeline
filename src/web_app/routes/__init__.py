from fastapi import APIRouter
from starlette.responses import RedirectResponse

from web_app.routes.api import pre_authorization_guidelines_ingest_route, pre_authorization_create_route

router = APIRouter()

router.include_router(pre_authorization_guidelines_ingest_route)
router.include_router(pre_authorization_create_route)


@router.get("/")
def docs():
    return RedirectResponse(url='/docs')
