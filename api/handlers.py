from fastapi import APIRouter, Body, Depends, HTTPException
from datetime import datetime, timedelta
from starlette import status

from api.models import connect_db, items
from api.forms import ImportsForm
from api.utils import datetime_valid, find_all_files, check_parentid
from api.documentation_data import doc_data

router = APIRouter()


@router.post('/imports',
             summary=doc_data['imports']['summary'],
             description=doc_data['imports']['description'])
def imports_handler(import_form: ImportsForm = Body(...), database=Depends(connect_db)):
    '''Обработчик imports'''
    for item in import_form.items:
        item_exists = database.query(items).filter(items.item_id == item.id).one_or_none()
        # проверка на существование и  смену типа
        if item_exists:
            if item_exists.type != item.type:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail={"code": 400,
                                            "message": "Can't update type"})
        else:
            # если не существует создаём новый
            item_exists = items()
        # заполняем поля
        item_exists.item_id = item.id
        item_exists.parent_id = item.parentId
        item_exists.size = item.size
        item_exists.type = item.type
        item_exists.url = item.url
        item_exists.created_at = import_form.updateDate

        # проверяем связи элемента
        check_parentid(item_exists, database)

        database.add(item_exists)
        # database.add(new_relation)
    database.commit()
    database.close()
    raise HTTPException(status_code=status.HTTP_200_OK, detail='Вставка или обновление прошли успешно.')


@router.delete('/delete/{id}',
               summary=doc_data['delete']['summary'],
               description=doc_data['delete']['description'])
def delete_handler(id: str, date: str, database=Depends(connect_db)):
    '''Обработчик delete'''
    if not datetime_valid(date):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"code": 400, "message": "Date is incorrect"})
    delete_item = database.query(items).filter(items.item_id == id).one_or_none()
    if delete_item:
        # удаляем сам элемент
        database.delete(delete_item)
        # удаляем все связи элемента
        find_all_files([], id, database, delete=True)
        delete_item.created_at = date
        # обновляем дату у всех элемнтов связанных с удалённым
        check_parentid(delete_item, database)

        database.commit()
        database.close()
        raise HTTPException(status_code=status.HTTP_200_OK, detail='Удаление прошло успешно.')
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Элемент не найден.')


@router.get('/nodes/{id}',
            summary=doc_data['nodes']['summary'],
            description=doc_data['nodes']['description'])
def nodes_handler(id: str, database=Depends(connect_db)):
    '''Обработчик nodes id'''
    node_item = database.query(items).filter(items.item_id == id.strip()).one_or_none()
    database.close()
    # проверка что item не None
    if node_item:
        response = {
            "id": node_item.item_id,
            "url": node_item.url,
            "parentId": node_item.parent_id,
            "type": node_item.type,
            "date": node_item.created_at,
            "size": node_item.size,
            "children": None
        }
        # рекурсивный поиск зависимостей и расчёт размера папки
        if node_item.type == "FOLDER":
            response["children"] = find_all_files([], node_item.item_id, database)
            response["size"] = sum([x.get("size", 0) for x in response["children"]])
        else:
            pass
        return response
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Элемент не найден.')


@router.get('/updates',
            summary=doc_data['updates']['summary'],
            description=doc_data['updates']['description'])
def updates_handler(date: str, database=Depends(connect_db)):
    '''Обработчик запроса updates'''
    if not datetime_valid(date):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"code": 400, "message": "Date is incorrect"})
    date = datetime.fromisoformat(date.replace('Z', '+00:00'))
    # return date, date - timedelta(days=1)
    response = []
    for item in database.query(items).all():
        item_date = datetime.fromisoformat(item.created_at.replace('Z', '+00:00'))
        if date - timedelta(days=1) <= item_date <= date:
            # 86400 секунд в 24 часах
            response.append(item)
    database.close()
    return response
