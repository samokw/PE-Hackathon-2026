from app import create_app
from app.database import db
from app.models.urls import Url
from app.models.users import User

app = create_app()

with app.app_context():
    db.create_tables([User, Url])
    # add json logging here
