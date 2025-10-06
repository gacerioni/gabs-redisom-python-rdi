import json
from typing import List
from models import ServiceAccount
from config import INDEX_PREFIX, INDEX_NAME

def create_sa(data: dict):
    sa = ServiceAccount(**data)
    sa.save()
    return sa.pk

def get_sa_by_id(sa_id: str):
    r = ServiceAccount.db()
    key = f"{INDEX_PREFIX}{sa_id}"
    raw = r.execute_command("JSON.GET", key)
    if not raw:
        raise KeyError("Not found")
    return json.loads(raw)

def search_by_email(email: str) -> List[ServiceAccount]:
    return ServiceAccount.find(ServiceAccount.email == email).all()

def search_by_name(term: str) -> List[ServiceAccount]:
    return ServiceAccount.find(ServiceAccount.name % term).all()

def search_global_raw(q: str):
    """
    Fallback global query (same behavior as `FT.SEARCH idx:sa:json 'Gabriel'`).
    Returns a list of dicts with the same shape as OM .dict() for rendering.
    """
    r = ServiceAccount.db()
    resp = r.execute_command(
        "FT.SEARCH", INDEX_NAME, q,
        "RETURN", 5,  # must equal number of paths below
        "$.id", "$.name", "$.email", "$.joined_at", "$.welcome_message",
        "LIMIT", 0, 50
    )
    out = []
    if isinstance(resp, list) and len(resp) > 1 and resp[0] > 0:
        i = 1
        while i < len(resp):
            key = resp[i]
            fields = resp[i + 1] if i + 1 < len(resp) else []
            doc = {}
            for j in range(0, len(fields), 2):
                path = fields[j]
                val = fields[j + 1] if j + 1 < len(fields) else None
                doc[path.lstrip("$.")] = val
            doc["_key"] = key
            out.append(doc)
            i += 2
    return out