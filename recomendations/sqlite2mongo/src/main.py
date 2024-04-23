import os
import sqlite3
import json
import requests
import uuid
from random import randint, shuffle

SQLITE_FILE = os.environ.get("SQLITE_FILE", "db.sqlite")
UGC_API_URL = os.environ.get(
    "UGC_API_URL", "http://localhost:60/api/v1/movies"
)

conn = sqlite3.connect(SQLITE_FILE)
cursor = conn.cursor()

cursor.execute("SELECT id, title FROM film_work")
films = cursor.fetchall()

# Генерация уникальных user_id
user_count = 100
user_ids = [str(uuid.uuid4()) for _ in range(user_count)]
user_for_tests = '3c8d0006-d12b-450c-808e-4c5639f2fb4d'
user_ids.append(user_for_tests)
shuffle(user_ids)  # Перемешиваем для случайного порядка


def generate_review():
    return {
        "review_id": str(uuid.uuid4()),
        "user_id": user_ids[randint(0, user_count - 1)],
        "article": "blah-blah",
        "text": "blah-blah-blah-blah-blah-blah",
        "likes": [generate_like() for _ in range(randint(1, 30))],
    }


def generate_like():
    return {
        "user_id": user_ids[randint(0, user_count - 1)],
        "rating": randint(1, 10),
    }


for film_id, title in films:
    data = {
        "id": film_id,
        "title": title,
        "reviews": [generate_review() for _ in range(randint(1, 30))],
        "likes": [generate_like() for _ in range(randint(1, 30))],
    }

    json_data = json.dumps(data)

    response = requests.post(
        UGC_API_URL,
        headers={"Content-Type": "application/json"},
        data=json_data,
    )

    if response.status_code == 200:
        print(f"Data for film {title} was successfully posted to the API.")
    else:
        print(
            f"Failed to post data for film {title}. Status code: {response.status_code}, response text: {response.text}"
        )

conn.close()
