import json

from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from fastapi import HTTPException, Depends
from json import dumps

from api.models import items
from starlette import status
from api.models import connect_db
from api.utils import datetime_valid

error400 = HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                         detail={"code": 400, "message": "Невалидная схема документа или входные данные не верны."})


class ItemForm(BaseModel):
    id: Optional[str] = None
    url: Optional[str] = ""
    parentId: Optional[str] = None
    size: Optional[int] = 0
    type: str

    class Config:
        json_loads = json.dumps

    @validator('id', always=True)
    def id_must_be_not_null(cls, check_id):
        if check_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"code": 400, "message": "id_must_be_not_null"})
        return check_id

    @validator('url', always=True)
    def url_len_less_255(cls, check_url):
        if len(check_url) > 255:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"code": 400, "message": "Url len must be less 256"})
        if check_url == "":
            return None
        return check_url

    @validator('parentId', always=True)
    def parent_must_be_folder(cls, check_parentid):
        if check_parentid == "" or check_parentid is None:
            return None
        database = connect_db()
        return check_parentid

    @validator('type', always=True)
    def type_and_size_validator(cls, check_type, values):
        check_size = values.get("size")
        check_url = values.get("url")
        if check_type not in ("FOLDER", "FILE"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"code": 400, "message": "Type is not 'FOLDER' or 'FILE'"})
        if check_type == "FOLDER" and check_size != 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"code": 400, "message": "Size of folder must be 0"})
        if check_type == "FOLDER" and not (check_url == "" or check_url is None):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"code": 400, "message": "FOLDER url must be '' or None"})
        if check_type == "FILE" and check_size == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"code": 400, "message": "Size of FILE must be greater than 0"})
        return check_type


class ImportsForm(BaseModel):
    items: list[ItemForm]
    updateDate: Optional[str] = ""

    class Config:
        json_loads = dumps

    @validator('updateDate', always=True)
    def check_data(cls, check_date):
        if not datetime_valid(check_date):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"code": 400, "message": "Date is incorrect"})
        return check_date
