FROM python:3.10.6-slim

ENV PYTHONUNBUFFERED 1

EXPOSE 8080
WORKDIR /api

COPY . /api
RUN pip install -r requirements.txt

CMD [ "uvicorn", "api.main:app", "--port", "8080", "--host", "0.0.0.0"]