FROM python:3.12-bookworm

RUN pip install poetry

WORKDIR /app
COPY ./pyproject.toml ./poetry.lock ./
RUN poetry install

COPY ./crypto_ingress ./crypto_ingress
CMD ["poetry", "run", "python", "-m", "crypto_ingress.server"]
