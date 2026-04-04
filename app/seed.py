import csv

from peewee import chunked

from app.database import db
from app.models.users import User

def load_csv(filepath):
    """
    Read a user CSV file and save each row to the database.

    The id values in the file are not saved; the database creates new ids for
    each user. That way the next user you add through the app gets a correct id.

    If the file includes an id column, this function also returns a dictionary
    that maps each old id from the file to the new id in the database (found by
    username and email). You can use that when loading other tables that still
    reference the old ids. If there is no id column, it returns an empty dict.
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
