FROM python:3.12-bookworm

RUN pip install poetry

WORKDIR /app
COPY ./pyproject.toml ./poetry.lock ./

ENV POETRY_VIRTUALENVS_CREATE=false
RUN poetry install

COPY ./crypto_ingress ./crypto_ingress
CMD ["python", "-m", "crypto_ingress.server"]
