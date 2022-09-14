from datetime import datetime
from api.models import connect_db, items, parents


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
            database.delete(database.query(parents.item_id == element.item_id).one_or_none())
    return response
