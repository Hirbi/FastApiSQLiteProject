from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from api.config import DATABASE_URL


def main():
    engine = create_engine(DATABASE_URL)
    session = Session(bind=engine.connect())

    session.execute("""
    create table items (
    item_id varchar(255) not null primary key,
    parent_id varchar(255), 
    size integer,
    type varchar(255) default FILE,
    url varchar(255),
    created_at varchar(255)
    )
    """)

    session.execute("""
        create table parents (
        id integer primary key,
        item_id varchar(255) not null references items,
        parent_id varchar(255) references items
        )
        """)

    session.close()


if __name__ == '__main__':
    main()
