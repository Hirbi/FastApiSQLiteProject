from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from api.handlers import router
from api.config import DATABASE_URL

import uvicorn


def create_table():
    engine = create_engine(DATABASE_URL)
    session = Session(bind=engine.connect())

    session.execute("""
    create table if not exists items (
    item_id varchar(255) not null primary key,
    parent_id varchar(255), 
    size integer,
    type varchar(255) default FILE,
    url varchar(255),
    created_at varchar(255)
    )
    """)

    session.close()


def get_app() -> FastAPI:
    create_table()
    app = FastAPI()
    app.include_router(router)
    return app


# uvicorn main:app
app = get_app()

# docker image build -t hirb/coolname .
# docker run -d -p 8080:8080 --restart always hirb/coolname
