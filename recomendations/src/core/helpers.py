from pydantic import BaseModel


def form_mongo_update_data(model: BaseModel, prefix: str):
    form_data = {}
    for field in model.__annotations__.keys():
        form_data[f'{prefix}{field}'] = getattr(model, field)
    return form_data
