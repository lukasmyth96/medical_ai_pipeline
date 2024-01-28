FROM python:3.10.7-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install poetry

RUN apt-get update && apt-get install -y ffmpeg

COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY ./src /app/src

ENV PYTHONPATH=/app/src

EXPOSE 80

CMD ["uvicorn", "src.web_app.main:app", "--host", "0.0.0.0", "--port", "80"]
