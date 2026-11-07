from app.db.database import engine, Base
from app.db import models

def init():
    Base.metadata.create_all(bind=engine)
    print("Database initialized: marketmind.db created with users + search_history tables")

if __name__ == "__main__":
    init()