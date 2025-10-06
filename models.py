from typing import Optional
from redis_om import JsonModel, Field
from config import redis, INDEX_NAME, GLOBAL_PREFIX, MODEL_PREFIX

class ServiceAccount(JsonModel):
    id: int = Field(index=True)
    name: str = Field(index=True, full_text_search=True)
    email: str = Field(index=True)
    joined_at: int = Field(index=True)
    welcome_message: Optional[str] = Field(index=True, full_text_search=True)

    class Meta:
        database = redis
        global_key_prefix = GLOBAL_PREFIX
        model_key_prefix  = MODEL_PREFIX
        index_name = INDEX_NAME