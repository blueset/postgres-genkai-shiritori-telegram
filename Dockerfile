# syntax=docker/dockerfile:1
FROM python:3-alpine
WORKDIR /genkai-shiritori
RUN apk update && \
    apk add --virtual build-deps gcc python3-dev musl-dev && \
    apk add postgresql-dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . /genkai-shiritori
CMD ["python3", "bot.py"]