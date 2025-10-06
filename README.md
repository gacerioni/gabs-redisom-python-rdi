# Redis OM Python Demo — Service Account Search

## Overview
This demo showcases how to use **Redis OM for Python** with **Flask** to query JSON data stored in Redis Stack.  
The app models "Service Accounts" and allows full-text and tag searches via Redis OM.

Redis OM acts as a thin abstraction over **RediSearch** and **RedisJSON**, automatically translating `.find()` queries into `FT.SEARCH` commands and hydrating results into Python models.

## Features
- Client-managed index (`ensure_index()` in app.py)
- Redis OM ORM abstraction with automatic hydration
- Centralized configuration (`config.py`)
- Flask UI for quick testing
- Debug endpoints for raw RediSearch access

## Project Structure
```
├── app.py              # Flask app with search routes and index management
├── config.py           # Central Redis connection and shared constants
├── models.py           # Redis OM model definitions
├── services.py         # Redis OM search logic + raw FT.SEARCH fallback
├── templates/
│   └── search.html     # Minimal UI for name/email search
└── requirements.txt    # Dependencies
```

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
(Ensure Redis Stack or Redis Cloud with JSON + Search modules is running.)

## Environment Setup
Create a `.env` file in the root with your connection string:
```
REDIS_OM_URL=redis://default:<password>@<host>:<port>/<db>
```

## Run the App
```bash
python app.py
```
Then open your browser to [http://127.0.0.1:5000](http://127.0.0.1:5000).

## How It Works
1. **Index Creation**
   - `ensure_index()` checks for `idx:sa:json` and creates it if missing:
     ```redis
     FT.CREATE idx:sa:json ON JSON PREFIX 1 solution_architects:id: SCHEMA
       $.id AS id NUMERIC
       $.name AS name TEXT
       $.email AS email TAG
       $.joined_at AS joined_at NUMERIC
       $.welcome_message AS welcome_message TEXT
     ```
2. **Redis OM Search**
   - Example:
     ```python
     ServiceAccount.find(ServiceAccount.name % "Gabriel").all()
     ```
     translates internally to:
     ```redis
     FT.SEARCH idx:sa:json '@name:Gabriel'
     ```
     Redis OM then hydrates JSON docs into Python objects.
3. **Hydration Process**
   - Redis OM fetches each result key via `JSON.GET` and maps it to a Pydantic model.

4. **Fallback / Debug**
   - `search_global_raw()` executes direct `FT.SEARCH` for troubleshooting.
   - `/debug/search_raw` endpoint exposes raw query results.

## Example Search Flow
1. User visits `/search?name=Gabriel`  
2. Redis OM issues a RediSearch query under the hood  
3. Matching Service Accounts are hydrated and displayed in the UI

## Notes
- The key prefix and model prefixes must match:
  - `GLOBAL_PREFIX = "solution_architects"`
  - `MODEL_PREFIX  = "id"`
  - `INDEX_PREFIX  = "solution_architects:id:"`
- Misaligned prefixes prevent Redis OM from hydrating search results.
- `config.py` ensures all constants are declared once and imported project-wide.

## Debug Endpoints
| Route | Description |
|-------|--------------|
| `/debug/indexes` | List all RediSearch indexes |
| `/debug/info` | Show FT.INFO for the current index |
| `/debug/search_raw?q=<term>` | Run a raw FT.SEARCH for debugging |

## License
MIT
