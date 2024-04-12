from motor.core import AgnosticClient

mongodb: AgnosticClient | None = None


def get_mongodb() -> AgnosticClient:
    if mongodb is None:
        raise RuntimeError('MongoDB client has not been defined.')
    return mongodb
