"""Parser input only; importing this controlled fixture is an error."""
from fastapi import FastAPI, Depends
from app.controls import authorize_export
from app.services import export_service, unknown_service

raise RuntimeError("STATIC_PARSE_ONLY: fixture must never execute")
app = FastAPI()


@app.get("/gap")
def gap():
    return export_service()


@app.get("/declared", dependencies=[Depends(authorize_export)])
def declared():
    return export_service()


@app.get("/unknown")
def unknown():
    return unknown_service()
