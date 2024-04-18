FROM python:3.11.0

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR on
ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV POETRY_VERSION 1.7.1

WORKDIR /auth-service

RUN apt-get update && apt-get install -y postgresql-client
RUN apt-get install -y redis-tools
RUN pip install poetry==$POETRY_VERSION
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \
  && poetry install --no-root
COPY . .
RUN chmod +x /auth-service/init.sh
CMD ["/auth-service/init.sh"]
