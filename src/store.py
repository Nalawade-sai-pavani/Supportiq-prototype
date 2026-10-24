"""Tiny file-based store for customer accounts and tickets (prototype only).
A real deployment would use PostgreSQL, as described in the architecture."""
import os, json, hmac, hashlib, datetime, re

DATA = "data"
USERS_FILE = os.path.join(DATA, "customers.json")
TICKETS_FILE = os.path.join(DATA, "tickets_db.json")


def _read(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _write(path, obj):
    os.makedirs(DATA, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


def _hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100_000).hex()


# ---------- customers ----------
def register_customer(username, password):
    username = username.strip().lower()
    if not re.fullmatch(r"[a-z0-9_]{3,20}", username):
        return False, "Username must be 3-20 letters, numbers or underscores."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    users = _read(USERS_FILE, {})
    if username in users:
        return False, "That username is taken."
    salt = os.urandom(16).hex()
    users[username] = {"salt": salt, "hash": _hash(password, salt)}
    _write(USERS_FILE, users)
    return True, "Account created. You can now log in."


def verify_customer(username, password, builtin=None):
    username = username.strip().lower()
    if builtin and username in builtin:
        return hmac.compare_digest(str(builtin[username]), password)
    u = _read(USERS_FILE, {}).get(username)
    if not u:
        return False
    return hmac.compare_digest(u["hash"], _hash(password, u["salt"]))


# ---------- tickets ----------
def add_ticket(customer, raw_text, res):
    tickets = _read(TICKETS_FILE, [])
    tid = max([t["id"] for t in tickets], default=1000) + 1
    tickets.append({
        "id": tid, "customer": customer,
        "created": datetime.datetime.now().isoformat(timespec="seconds"),
        "raw_text": raw_text, "masked_text": res["masked_text"],
        "intent": res["intent"], "confidence": round(res["confidence"], 3),
        "priority": res["priority"], "draft": res["reply"],
        "sources": res["sources"], "reason": res.get("reason", ""),
        "status": "Open", "reply": None, "agent": None, "replied_at": None})
    _write(TICKETS_FILE, tickets)
    return tid


def list_tickets(customer=None):
    tickets = _read(TICKETS_FILE, [])
    if customer:
        tickets = [t for t in tickets if t["customer"] == customer]
    return tickets


def update_ticket(tid, **fields):
    tickets = _read(TICKETS_FILE, [])
    for t in tickets:
        if t["id"] == tid:
            t.update(fields)
    _write(TICKETS_FILE, tickets)