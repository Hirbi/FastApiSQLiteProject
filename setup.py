from setuptools import setup

setup(
    name='FastAPI_app',
    version='0.0.1',
    Author='Roman Shokhrin',
    author_email='romanshohrin@yandex.ru',
    description='FastAPI app',
    install_requires=[
        'fastapi',
        'uvicorn',
        'SQLAlchemy',
        'pytest',
        'requests'
    ],
    scripts=['app/main.py', 'scripts/create_db.py']
)
