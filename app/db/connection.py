from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = None
Session = None

def init_db(db_url):
    global engine, Session
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)

def get_db():
    if Session is None:
        raise RuntimeError("Database is not yet initialized. Call init_db first.")
    return Session()
