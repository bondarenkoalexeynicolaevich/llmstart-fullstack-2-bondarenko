"""Корневой роутер API v1."""

from fastapi import APIRouter

from backend.api.auth_web import router as auth_web_router
from backend.api.data_query_web import router as data_query_web_router
from backend.api.dialog import router as dialog_router
from backend.api.flow_modules import router as flow_modules_router
from backend.api.flows_web import router as flows_web_router
from backend.api.participant_dialog_web import router as participant_dialog_web_router
from backend.api.participant_submissions import router as participant_submissions_router
from backend.api.submissions import router as submissions_router
from backend.api.voice import router as voice_router

router = APIRouter(prefix="/v1", tags=["v1"])
router.include_router(auth_web_router)
router.include_router(
    dialog_router, prefix="/dialog-messages", tags=["dialog-messages"]
)
router.include_router(voice_router, prefix="/voice/dialog-messages")
router.include_router(submissions_router, prefix="/submissions", tags=["submissions"])
router.include_router(flow_modules_router, tags=["flows"])
router.include_router(flows_web_router)
router.include_router(data_query_web_router)
router.include_router(participant_submissions_router, tags=["participants"])
router.include_router(participant_dialog_web_router)
