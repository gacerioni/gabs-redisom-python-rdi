# Centralized configuration
import os
from dotenv import load_dotenv
from redis_om import get_redis_connection

load_dotenv()

REDIS_OM_URL = os.getenv("REDIS_OM_URL")

redis = get_redis_connection(
    url=REDIS_OM_URL,
    host=None if REDIS_OM_URL else "localhost",
    port=None if REDIS_OM_URL else 6379,
    decode_responses=True,
)

# ---- Shared constants ----
INDEX_NAME   = "idx:sa:json"
INDEX_PREFIX = "solution_architects:id:"
GLOBAL_PREFIX = "solution_architects"
MODEL_PREFIX  = "id"