"""Корневой роутер API v1."""

from fastapi import APIRouter

from backend.api.dialog import router as dialog_router
from backend.api.flow_modules import router as flow_modules_router
from backend.api.participant_submissions import router as participant_submissions_router
from backend.api.submissions import router as submissions_router

router = APIRouter(prefix="/v1", tags=["v1"])
router.include_router(
    dialog_router, prefix="/dialog-messages", tags=["dialog-messages"]
)
router.include_router(submissions_router, prefix="/submissions", tags=["submissions"])
router.include_router(flow_modules_router, tags=["flows"])
router.include_router(participant_submissions_router, tags=["participants"])
