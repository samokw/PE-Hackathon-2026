from app import create_app
from app.database import db
from app.models.users import User

app = create_app()

with app.app_context():
    db.create_tables([User])
    # add json logging here 
