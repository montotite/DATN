import pandas
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter()

templates = Jinja2Templates(directory="views/html")


@router.get("/", response_class=HTMLResponse)
def read_item(request: Request):
    return templates.TemplateResponse(request, name="index.html")


@router.get("/devices", response_class=HTMLResponse)
def read_item(request: Request):
    return templates.TemplateResponse(request, name="device.html")


@router.get("/device/{id}", response_class=HTMLResponse)
def read_item(request: Request, id: UUID):
    print(id)
    return templates.TemplateResponse(request, name="device.html")


@router.get("/warnings", response_class=HTMLResponse)
def read_item(request: Request):
    return templates.TemplateResponse(request, name="warning.html")
