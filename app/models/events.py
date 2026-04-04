from peewee import AutoField, CharField, DateTimeField, ForeignKeyField, TextField

from app.database import BaseModel
from app.models.urls import Url
from app.models.users import User


class UrlEvent(BaseModel):
    id = AutoField()
    url = ForeignKeyField(Url, backref="events")
    user = ForeignKeyField(User, backref="events")
    event_type = CharField()
    timestamp = DateTimeField()
    details = TextField()
