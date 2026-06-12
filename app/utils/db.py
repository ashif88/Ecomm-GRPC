from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os


SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///ecomm.db')

# Create the SQLAlchemy engine that connects to the database
# For SQLite, we want to allow concurrent access from thread pools
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# Create a session maker bound to this engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a scoped session
db_session = scoped_session(SessionLocal)

# Create the base class for models (like db.Model in Flask)
Base = declarative_base()
Base.query = db_session.query_property()

# Custom db object to use with db.Model
class db:
    Model = Base
    engine = engine
    SessionLocal = SessionLocal
    session = db_session

