from datetime import datetime
from api.models import connect_db, items, parents
from fastapi import HTTPException
from starlette import status


def datetime_valid(dt_str):
    '''проверка на совместимость даты с ISO 8601'''
    try:
        datetime.fromisoformat(dt_str)
    except:
        try:
            datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except:
            return False
        return True
    return True


def find_all_files(response: list, item_id, database, delete=False):
    """поиск всех зависимостей папки"""
    for element in database.query(items).filter(item_id == items.parent_id).all():
        response.append(
            {
                "id": element.item_id,
                "url": element.url,
                "parentId": element.parent_id,
                "size": element.size,
                "type": element.type,
                "date": element.created_at
            }
        )
        if element.type == "FOLDER":
            response[-1]["children"] = []
            find_all_files(response[-1]["children"], element.item_id, database, delete)
        if delete:
            database.delete(element)
            database.delete(database.query(parents).filter(parents.item_id == element.item_id).one_or_none())
    return response


def check_parentid_and_type(item, item_exists, database):
    # проверка, что parentId это папка
    if item.parentId is not None:
        if database.query(parents).filter(parents.parent_id == item.parentId).one_or_none() is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"code": 400,
                                        "message": "ParentId must be a folder"})
    # проверка на изменение type
    if item_exists.type != item.type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"code": 400,
                                    "message": "Can't update type"})
