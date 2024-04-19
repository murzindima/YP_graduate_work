# Скрипт наполняет данными MongoDB сервиса UGC через API UGC

## Что он делает

- селектит и базы sqlite, таблицы film_work  -- id и title 
- рандомно генерит UUID-ы и лайки
- крафтит запрос из всего этого под схему

```json
 {
  "id": "string",
  "title": "string",
  "reviews": [
    {
      "review_id": "string",
      "user_id": "string",
      "article": "string",
      "text": "string",
      "likes": []
    }
  ],
  "likes": [
    {
      "user_id": "string",
      "rating": 0
    }
  ]
}
```

- и пуляет пост запрос в /api/v1/movies сервиса UGC

## конфиг

- переменная окружения SQLITE_FILE -- db.sqlite которую нам давали в теорию (дефолт -- db.sqlite в каталоге с скриптом)
- переменная окружения  UGC_API_URL -- урла куда заливать фильмы (дефолт -- <http://localhost:60/api/v1/movies>)
