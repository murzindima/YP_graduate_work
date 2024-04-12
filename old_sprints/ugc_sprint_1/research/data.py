import math
import random
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from more_itertools import chunked


@dataclass
class PlaybackMark:
    timestamp: datetime = datetime.min
    user_id: UUID = uuid4()
    movie_id: UUID = uuid4()
    view_duration: int = 0

    def to_dict(self):
        return {
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": str(self.user_id),
            "movie_id": str(self.movie_id),
            "view_duration": self.view_duration,
        }


class PlaybackMarks(list[PlaybackMark]):
    def __init__(self, total: int, user_count: int, movie_count: int):
        super().__init__(PlaybackMark() for _ in range(total))
        self._set_users(user_count)
        self._set_movie(movie_count)
        self._set_view_durations()

    def to_dict(self):
        return [view.to_dict() for view in self]

    @property
    def _map_by_user_movie(self):
        dict_: dict[str, list[PlaybackMark]] = defaultdict(list)
        for view in self:
            dict_[str(view.user_id) + str(view.movie_id)].append(view)
        return dict_

    def _set_users(self, user_count: int):
        user_ids = [uuid4() for _ in range(user_count)]
        chunk_count = math.ceil(len(self) / user_count)
        for user_id_idx, user_chunk in enumerate(chunked(self, chunk_count)):
            for user in user_chunk:
                user.user_id = user_ids[user_id_idx]

    def _set_movie(self, movie_count: int):
        movie_ids = [uuid4() for _ in range(movie_count)]
        chunk_count = math.ceil(len(self) / movie_count)
        for movie_id_idx, movie_chunk in enumerate(chunked(self, chunk_count)):
            for movie in movie_chunk:
                movie.movie_id = movie_ids[movie_id_idx]

    def _set_view_durations(self):
        for views in self._map_by_user_movie.values():
            start_datetime = datetime(2024, 1, 1, 0, 0, 0)
            for view in views:
                view.timestamp = start_datetime
                view.view_duration += random.randint(1, 5)
                start_datetime += timedelta(seconds=5)
