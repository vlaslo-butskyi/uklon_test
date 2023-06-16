FROM python:3.11.1-slim

RUN apt-get update && \
    apt-get install -y libpq-dev gcc

ENV TZ=Europe/Kiev
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi --sync

EXPOSE 8080

ENV FLASK_APP /app/src/__init__.py

CMD ["/bin/bash", "-c", "poetry run flask db upgrade;poetry run serve"]