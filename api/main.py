from fastapi import FastAPI
from api.handlers import router

import uvicorn


def get_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    return app


# uvicorn main:app
app = get_app()

# docker image build -t hirb/coolname .
# docker run -d -p 8080:8080 --restart always hirb/coolname
