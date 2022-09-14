from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from enum import Enum

from api.config import DATABASE_URL

Base = declarative_base()


def connect_db():
    engine = create_engine(DATABASE_URL, connect_args={})
    session = Session(bind=engine.connect())
    return session


class type(Enum):
    FILE = 'FILE'
    FOLDER = 'FOLDER'


class items(Base):
    __tablename__ = 'items'
    item_id = Column(String, primary_key=True, unique=True)
    import_id = Column(Integer, unique=False)
    parent_id = Column(String, unique=False)
    size = Column(Integer)
    type = Column(String)
    url = Column(String(255), max_lenght=256)
    created_at = Column(String, default=datetime.utcnow())


class imports(Base):
    __tablename__ = 'imports'

    import_id = Column(Integer, ForeignKey('items.import_id'), primary_key=True, autoincrement=True)


class parents(Base):
    __tablename__ = 'parents'
    id = Column(Integer, primary_key=True)
    import_id = Column(Integer, ForeignKey('items.import_id'), unique=False)
    item_id = Column(String, ForeignKey('items.item_id'))
    parent_id = Column(String, ForeignKey('items.item_id'))
