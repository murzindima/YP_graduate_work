FROM python:3.11.0

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR on
ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV POETRY_VERSION 1.7.1

WORKDIR /usr/src/cron

RUN pip install poetry==$POETRY_VERSION
COPY pyproject.toml ./
RUN poetry config virtualenvs.create false \
  && poetry install --no-root

RUN apt-get update
RUN apt-get -y install cron

RUN crontab -l | { cat; echo "* 1 * * * /usr/local/bin/python  /usr/src/cron/cron.py 2>/usr/src/cron/logs/cron.log"; } | crontab -


COPY . .

CMD ["bash", "start.sh"]



