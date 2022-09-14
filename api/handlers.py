import datetime

from fastapi import APIRouter, Body, Depends, HTTPException
import uuid
from starlette import status
from api.models import connect_db, items, imports, parents
from api.forms import ImportsForm, ItemForm, error400
from api.utils import datetime_valid, find_all_files
from starlette.responses import Response

router = APIRouter()


@router.get('/')
def index():
    return {'status': 200}


@router.post('/imports')
def imports_handler(import_form: ImportsForm = Body(..., embed=True), database=Depends(connect_db)):
    # добавляем новую imports в базу данных
    database.add(imports())
    import_id = database.query(imports).all()[-1].import_id  # получаем номер imports
    for item in import_form.items:
        item_exists = database.query(items).filter(items.item_id == item.id).one_or_none()
        if item_exists:
            if item_exists.type != item.type:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail={"code": 400,
                                            "message": "Can't update type"})
            item_exists.import_id = import_id
            item_exists.parent_id = item.parentId
            item_exists.size = item.size
            item_exists.url = item.url
            item_exists.created_at = import_form.updateDate
        else:
            item_exists = items(
                item_id=item.id,
                import_id=import_id,  # new_imports.import_id,
                parent_id=item.parentId,
                size=item.size,
                type=item.type,
                url=item.url,
                created_at=import_form.updateDate
            )
        new_relation = parents(import_id=import_id, item_id=item.id, parent_id=item.parentId)
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
