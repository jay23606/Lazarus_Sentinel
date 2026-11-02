from fastapi import APIRouter
from app.services import export_service

inherited = APIRouter()


@inherited.get("/export")
def inherited_export():
    return export_service()
