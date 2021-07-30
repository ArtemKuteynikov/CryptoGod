from app import db, create_app
import os
import time

os.environ["TZ"] = "Europe/Moscow"
time.tzset()

db.create_all(app=create_app())
app = create_app()

