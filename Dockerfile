FROM tiangolo/uvicorn-gunicorn-fastapi:latest

COPY ./app/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY ./app /app