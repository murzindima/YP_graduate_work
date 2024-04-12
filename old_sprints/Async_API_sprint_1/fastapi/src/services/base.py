import json
from typing import Type, Any, Union
from urllib.parse import urlencode

from elasticsearch import AsyncElasticsearch, NotFoundError
from pydantic import BaseModel
from redis.asyncio import Redis
from fastapi import Request

from queries.base import BaseFilter

CACHE_EXPIRE_IN_SECONDS = 60 * 5
CACHE_NAMESPACE = "api_response"


class BaseService[M: BaseModel]:
    """
    Base service class for interacting with Elasticsearch and Redis for data retrieval and caching.

    Parameters:
    - redis (Redis): An instance of the Redis client for caching purposes.
    - elastic (AsyncElasticsearch): An instance of the AsyncElasticsearch client for interacting with Elasticsearch.
    - model_class (Type[M]): The Pydantic BaseModel subclass representing the data model for this service.
    - index (str): The Elasticsearch index to operate on.
    """

    def __init__(
            self,
            request: Request,
            redis: Redis,
            elastic: AsyncElasticsearch,
            model_class: Type[M],
            index: str
    ):
        self.request = request
        self.redis = redis
        self.elastic = elastic
        self.model_class = model_class
        self.index = index

    async def get_by_id(self, model_id: str) -> M | None:
        """
        Retrieve a model by its unique identifier.

        Parameters:
        - model_id (str): The unique identifier of the model.

        Returns:
        - An instance of the model if found, otherwise None.
        """
        cache_key = self._generate_cache_key(self.request)
        model = await self._from_cache(cache_key)
        if not model:
            model = await self._get_model_from_elastic(model_id)
            if not model:
                return None
            await self._put_to_cache(cache_key, model)

        return model

    async def get_all(self, model_filter: BaseFilter) -> list[M]:
        """
        Retrieve multiple models based on the provided filter.

        Parameters:
        - model_filter (BaseFilter): An instance of BaseFilter containing filtering parameters.

        Returns:
        - A list of model instances that match the filter criteria.
        """
        cache_key = self._generate_cache_key(self.request)
        models = await self._from_cache(cache_key)
        if not models:
            models = await self._get_all_from_elastic(model_filter)
            if not models:
                return []
            await self._put_to_cache(cache_key, models)

        return models

    async def _get_model_from_elastic(self, model_id: str) -> M | None:
        """
        Retrieve a model from Elasticsearch by its unique identifier.

        Parameters:
        - model_id (str): The unique identifier of the model.

        Returns:
        - An instance of the model if found, otherwise None.
        """
        try:
            doc = await self.elastic.get(index=self.index, id=model_id)
        except NotFoundError:
            return None
        return self.model_class(**doc["_source"])

    async def _get_all_from_elastic(self, model_filter: BaseFilter) -> list[M]:
        """
        Retrieve multiple models from Elasticsearch based on the provided filter.

        Parameters:
        - model_filter (BaseFilter): An instance of BaseFilter containing filtering parameters.

        Returns:
        - A list of model instances that match the filter criteria.
        """
        query_body = await self._make_query(model_filter)
        try:
            doc = await self.elastic.search(index=self.index, body=query_body)
        except NotFoundError:
            return []
        return [self.model_class(**model["_source"]) for model in doc["hits"]["hits"]]

    @staticmethod
    async def _enrich_query_with_search(model_filter: BaseFilter, query_body: dict[str, Any], field: str) -> dict[str, Any]:
        """
        Enrich the Elasticsearch query with a fuzzy search.

        Parameters:
        - model_filter (BaseFilter): An instance of BaseFilter containing search parameters.
        - query_body (dict[str, Any]): The Elasticsearch query body.
        - field (str): The field to perform the fuzzy search on.

        Returns:
        - The modified Elasticsearch query body.
        """
        if model_filter.query:
            query_body["query"]["bool"]["must"].append(
                {
                    "fuzzy": {
                        field: {
                            "value": model_filter.query,
                            "fuzziness": "AUTO"
                        },
                    },
                },
            )
        return query_body

    async def _make_query(self, model_filter: BaseFilter) -> dict[str, Any]:
        """
        Construct the Elasticsearch query body based on the provided filter with pagination.

        Parameters:
        - model_filter (BaseFilter): An instance of BaseFilter containing filtering parameters.

        Returns:
        - The Elasticsearch query body.
        """
        query_body = {
            "query": {
                "bool": {
                    "must": [],
                },
            },
            "size": model_filter.page_size,
            "from": (model_filter.page_number - 1) * model_filter.page_size,
        }
        return query_body

    @staticmethod
    def _generate_cache_key(request: Request) -> str:
        """
        Generate a unique cache key based on the request's path and query parameters.
        """
        namespace = CACHE_NAMESPACE
        path = request.url.path
        sorted_query_params = sorted(request.query_params.items())
        query_string = urlencode(sorted_query_params)

        return f"{namespace}:{path}?{query_string}"

    async def _from_cache(self, cache_key: str) -> Union[M, list[M]] | None:
        """
        Retrieve a model or list of models from the Redis cache.

        Parameters:
        - cache_key (str): The unique key for retrieving the data.

        Returns:
        - An instance of the model or a list of model instances if found in the cache, otherwise None.
        """
        data = await self.redis.get(cache_key)
        if not data:
            return None

        try:
            deserialized_data = json.loads(data)
        except json.JSONDecodeError:
            return None

        if isinstance(deserialized_data, list):
            return [self.model_class.model_validate_json(item) for item in deserialized_data]

        return self.model_class.model_validate_json(deserialized_data)

    async def _put_to_cache(self, cache_key: str, model: M | list[M]):
        """
        Put a model or list of models into the Redis cache.

        Parameters:
        - model (M | list[M]): An instance of the model or a list of models to be cached.
        """
        if isinstance(model, list):
            serialized_data = json.dumps([m.model_dump_json() for m in model])
        else:
            serialized_data = model.model_dump_json()

        await self.redis.set(cache_key, serialized_data, CACHE_EXPIRE_IN_SECONDS)
