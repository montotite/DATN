import pandas
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from utils import *
from helpers import get_db


router = APIRouter()

templates = Jinja2Templates(directory="views/html")


@router.get("/", response_class=HTMLResponse)
def read_item(request: Request):
    return templates.TemplateResponse(request, name="index.html")


@router.get("/devices", response_class=HTMLResponse)
def read_item(request: Request):
    return templates.TemplateResponse(request, name="device.html")


@router.get("/device/{id}", response_class=HTMLResponse)
def read_item(request: Request, id: UUID, db=Depends(get_db)):
    db = Crud(db)
    info = db.get_device_info(id)
    if info["additional_info"] != None:
        info["additional_info"] = json.loads(info["additional_info"])
    return templates.TemplateResponse(request, name="device-detail.html", context=info)


@router.get("/warnings", response_class=HTMLResponse)
def read_item(request: Request):
    return templates.TemplateResponse(request, name="warning.html")
