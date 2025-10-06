import os
from flask import Flask, request, jsonify, render_template
from redis.exceptions import ResponseError
from models import ServiceAccount
from services import get_sa_by_id, search_by_email, search_by_name, search_global_raw
from config import INDEX_NAME, INDEX_PREFIX

app = Flask(__name__)

def index_exists(r) -> bool:
    try:
        r.execute_command("FT.INFO", INDEX_NAME)
        return True
    except ResponseError:
        return False

def ensure_index():
    r = ServiceAccount.db()
    if index_exists(r):
        print(f"[ensure_index] Found existing index: {INDEX_NAME}")
        return

    print(f"[ensure_index] Creating index: {INDEX_NAME}")
    try:
        r.execute_command(
            "FT.CREATE", INDEX_NAME,
            "ON", "JSON",
            "PREFIX", "1", INDEX_PREFIX,
            "SCHEMA",
            "$.id",              "AS", "id",              "NUMERIC",
            "$.name",            "AS", "name",            "TEXT",
            "$.email",           "AS", "email",           "TAG",
            "$.joined_at",       "AS", "joined_at",       "NUMERIC",
            "$.welcome_message", "AS", "welcome_message", "TEXT",
        )
        print(f"[ensure_index] ✅ Created index {INDEX_NAME}")
    except ResponseError as e:
        if "exists" in str(e):
            print(f"[ensure_index] Already exists: {INDEX_NAME}")
        else:
            raise

# Build/verify index once at startup
ensure_index()

@app.route("/")
def home():
    return render_template("search.html", results=None)

@app.route("/search")
def search():
    name  = (request.args.get("name") or "").strip()
    email = (request.args.get("email") or "").strip()
    results = []

    if name:
        results = [s.dict() for s in search_by_name(name)]
        if not results:
            print(f"[debug] OM returned 0; trying raw FT.SEARCH '{name}'")
            results = search_global_raw(name)
    elif email:
        results = [s.dict() for s in search_by_email(email)]

    return render_template("search.html", results=results)

@app.route("/sa/<sa_id>")
def get_sa(sa_id):
    try:
        doc = get_sa_by_id(sa_id)
        return jsonify(doc)
    except Exception:
        return {"error": "Not found"}, 404

# --- Debug endpoints ---
@app.route("/debug/indexes")
def list_indexes():
    try:
        res = ServiceAccount.db().execute_command("FT._LIST")
        return jsonify(res)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/debug/info")
def index_info():
    idx = request.args.get("i", INDEX_NAME)
    try:
        res = ServiceAccount.db().execute_command("FT.INFO", idx)
        info = {}
        for i in range(0, len(res), 2):
            k = res[i]
            v = res[i + 1] if i + 1 < len(res) else None
            info[k] = v
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/debug/search_raw")
def search_raw():
    q = request.args.get("q", "*")
    try:
        data = search_global_raw(q)
        return jsonify({"count": len(data), "docs": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ----------------------------------

if __name__ == "__main__":
    app.run(debug=True)