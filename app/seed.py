import csv

from peewee import chunked

from app.database import db
from app.models.users import User

def load_csv(filepath):
    """
    Load users from CSV. Does not insert ``id`` — Postgres assigns ids so the
    sequence stays valid.

    If the CSV has an ``id`` column, returns a mapping ``{old_csv_id: new_db_id}``
    (match on username + email) for remapping foreign keys in other seed files.
    Otherwise returns an empty dict.
    """
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    required = ("username", "email", "created_at")
    insert_rows = []
    for i, row in enumerate(rows, start=2):
        payload = {}
        for key in required:
            val = (row.get(key) or "").strip()
            if not val:
                raise ValueError(f"row {i}: missing or empty {key!r}")
            payload[key] = val
        insert_rows.append(payload)

    with db.atomic():
        for batch in chunked(insert_rows, 100):
            User.insert_many(batch).execute()

    mapping = {}
    if rows and "id" in fieldnames:
        for row in rows:
            raw_id = (row.get("id") or "").strip()
            if not raw_id:
                raise ValueError("CSV has id column but a row has an empty id")
            old_id = int(raw_id)
            u = User.get(
                (User.username == row["username"].strip())
                & (User.email == row["email"].strip())
            )
            mapping[old_id] = u.id

    return mapping
