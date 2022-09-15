import datetime
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Body, Depends, HTTPException
import uuid
from starlette import status
from api.models import connect_db, items, parents
from api.forms import ImportsForm, ItemForm, error400
from api.utils import datetime_valid, find_all_files, check_parentid_and_type
from starlette.responses import Response

router = APIRouter()


@router.get('/')
def index():
    return {'status': 200}


@router.post('/imports')
def imports_handler(import_form: ImportsForm = Body(...), database=Depends(connect_db)):
    # добавляем новую imports в базу данных
    for item in import_form.items:
        item_exists = database.query(items).filter(items.item_id == item.id).one_or_none()
        if item_exists:
            check_parentid_and_type(item, item_exists, database)
            '''
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
                                            '''
        else:
            # если не существует создаём новый
            item_exists = items()
        item_exists.item_id = item.id
        item_exists.parent_id = item.parentId
        item_exists.size = item.size
        item_exists.type = item.type
        item_exists.url = item.url
        item_exists.created_at = import_form.updateDate
        new_relation = parents(item_id=item.id, parent_id=item.parentId)
        database.add(item_exists)
        database.add(new_relation)
    database.commit()
    raise HTTPException(status_code=status.HTTP_200_OK, detail='Вставка или обновление прошли успешно.')


@router.delete('/delete/{id}')
def delete_handler(id: str, datetime: str = datetime.datetime.now().isoformat(), database=Depends(connect_db)):
    if not datetime_valid(datetime):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"code": 400, "message": "Date is incorrect"})
    delete_item = database.query(items).filter(
        items.item_id == id and items.created_at == datetime).one_or_none()
    if delete_item:
        # удаляем сам элемент
        database.delete(delete_item)
        database.delete(database.query(parents).filter(parents.item_id == delete_item.item_id).one_or_none())
        # удаляем все связи элемента
        find_all_files([], id, database, delete=True)
        database.commit()
        raise HTTPException(status_code=status.HTTP_200_OK, detail='Удаление прошло успешно.')
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Элемент не найден.')


@router.get('/notes/{id}')
def nodes_handler(id: str, database=Depends(connect_db)):
    node_item = database.query(items).filter(items.item_id == id).one_or_none()
    if node_item:
        response = {
            "id": node_item.item_id,
            "url": node_item.url,
            "parentId": node_item.parent_id,
            "size": node_item.size,
            "type": node_item.type,
            "date": node_item.created_at,
        }
        if node_item.type == "FOLDER":
            response["children"] = find_all_files([], node_item.item_id, database)
        return response
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Элемент не найден.')
