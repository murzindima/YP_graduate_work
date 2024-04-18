import os
import sqlite3
import json
import requests
import uuid
from random import randint

SQLITE_FILE = os.environ.get("SQLITE_FILE", "db.sqlite")
UGC_API_URL = os.environ.get("UGC_API_URL", 'http://localhost:60/api/v1/movies')

conn = sqlite3.connect(SQLITE_FILE)
cursor = conn.cursor()

cursor.execute("SELECT id, title FROM film_work")
films = cursor.fetchall()


def generate_review():
    return {
        "review_id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "article": "blah-blah",
        "text": "blah-blah-blah-blah-blah-blah",
        "likes": [generate_like() for _ in range(randint(1, 30))],
    }


def generate_like():
    return {
        "user_id": str(uuid.uuid4()),
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

    response = requests.post(UGC_API_URL, headers={'Content-Type': 'application/json'}, data=json_data)

    if response.status_code == 200:
        print(f"Data for film {title} was successfully posted to the API.")
    else:
        print(f"Failed to post data for film {title}. Status code: {response.status_code}, response text: {response.text}")

conn.close()
