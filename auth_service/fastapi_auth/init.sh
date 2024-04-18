#!/bin/bash
set -e

# Ждем, пока база данных станет доступной
until PGPASSWORD=$POSTGRES_PASSWORD pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

# Выполняем миграции
poetry run alembic upgrade head

# Проверяем, существует ли роль admin
ADMIN_ROLE_EXISTS=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -tAc "SELECT EXISTS (SELECT 1 FROM role WHERE title = 'admin');")

if [ "$ADMIN_ROLE_EXISTS" = "f" ]; then
  # Генерируем новый UUID для роли admin
  ADMIN_ROLE_ID=$(python -c "import uuid; print(str(uuid.uuid4()))")

  # Выполняем запрос SQL для создания роли admin
  PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "INSERT INTO role (id, title, description, created_at, modified_at) VALUES ('$ADMIN_ROLE_ID', 'admin', 'Повелитель всего', NOW(), NOW());"

  # Генерируем новый UUID для пользователя
  CUSTOM_USER_ID=$(python -c "import uuid; print(str(uuid.uuid4()))")

  # Генерируем хэшированный пароль с использованием passlib
  SUPERUSER_HASHED_PASSWORD=$(python -c "from passlib.hash import bcrypt; print(bcrypt.hash('$SUPERUSER_PASSWORD'))")

  # Выполняем запрос SQL для создания пользователя
  PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "INSERT INTO users (id, username, email, hashed_password, first_name, last_name, is_active, created_at, modified_at) VALUES ('$CUSTOM_USER_ID', '$SUPERUSER_NAME', '$SUPERUSER_EMAIL', '$SUPERUSER_HASHED_PASSWORD', '$SUPERUSER_FIRST_NAME', '$SUPERUSER_LAST_NAME', true, NOW(), NOW());"

  # Генерируем новый UUID для роли пользователя админ
  USER_ROLE_ID=$(python -c "import uuid; print(str(uuid.uuid4()))")

  # Выполняем запрос SQL для создания записи роль-пользователь для admin
  PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "INSERT INTO user_role (id, user_id, role_id, expire_at, is_active, created_at, modified_at) VALUES ('$USER_ROLE_ID', '$CUSTOM_USER_ID', '$ADMIN_ROLE_ID', null, true, NOW(), NOW());"

fi

# Ждем, пока Redis станет доступным
until redis-cli -h $AUTH_REDIS_HOST -p $AUTH_REDIS_PORT ping; do
  >&2 echo "Redis is unavailable - sleeping"
  sleep 1
done

# Запускаем FastAPI-сервер
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b :$AUTH_FASTAPI_PORT main:app
