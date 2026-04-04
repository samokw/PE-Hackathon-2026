from peewee import AutoField, BooleanField, CharField, DateTimeField, ForeignKeyField

from app.database import BaseModel
from app.models.users import User


class Url(BaseModel):
    id = AutoField()
    user = ForeignKeyField(User, field="id", backref="urls")
    short_code = CharField()
    original_url = CharField()
    title = CharField()
    is_active = BooleanField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
