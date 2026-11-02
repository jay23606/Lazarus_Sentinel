from typing import Annotated
from fastapi import FastAPI, Depends, Security
from app.controls import authenticate, authorize_export
from app.services import export_service, public_service
from app.routes import inherited

app = FastAPI()
app.include_router(inherited, prefix="/inherited", dependencies=[Depends(authorize_export)])


@app.get("/weak")
def weak_export():
    return export_service()


@app.get("/protected")
def protected_export(permission=Depends(authorize_export)):
    return export_service()


@app.get("/authenticated")
def authenticated_export(user=Depends(authenticate)):
    return export_service()


@app.get("/annotated")
def annotated_export(permission: Annotated[str, Security(authorize_export)]):
    return export_service()


@app.get("/public")
def public_status():
    return public_service()


def dynamic_export():
    return export_service()


app.add_api_route("/dynamic", dynamic_export)
