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
                "type": element.type,
                "date": element.created_at,
                "size": element.size,
                "children": None
            }
        )
        if element.type == "FOLDER":
            response[-1]["children"] = []
            find_all_files(response[-1]["children"], element.item_id, database, delete)
            response[-1]["size"] = sum([x.get("size", 0) for x in response[-1]["children"]])
        if delete:
            database.delete(element)
    return response


def check_parentid(item: items, database, check=True):
    # проверка, что parentId это папка
    if item.parent_id is not None:
        parent = database.query(items).filter(
                items.item_id == item.parent_id and items.type == "FOLDER").one_or_none()
        if parent is None and check:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail={"code": 400,
                                        "message": "ParentId must be a folder"})

        parent.created_at = item.created_at

        if parent.parent_id is not None:
            check_parentid(parent, database, check)

    return
