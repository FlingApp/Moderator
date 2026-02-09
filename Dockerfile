FROM python:3.12-slim-bookworm AS python-base

ENV PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv" \
    POETRY_HOME="/opt/poetry"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base AS builder-base
RUN pip install poetry

WORKDIR $PYSETUP_PATH

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.in-project true && \
    poetry install --without dev,test --no-root

FROM python-base AS production
WORKDIR /app

COPY --from=builder-base $VENV_PATH $VENV_PATH

COPY ./src /app
COPY pyproject.toml poetry.lock ./

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]