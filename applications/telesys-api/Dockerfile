FROM python:3.12-bookworm

ENV PYTHONUNBUFFERED=1
RUN pip install poetry

WORKDIR /app
COPY ./pyproject.toml ./poetry.lock ./

ENV POETRY_VIRTUALENVS_CREATE=false
RUN poetry install

COPY ./telesys ./telesys
CMD ["uvicorn", "telesys.server:app", "--host", "0.0.0.0"]
