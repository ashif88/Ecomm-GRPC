from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL', '')

# Create the SQLAlchemy engine that connects to the database
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# Create a session maker bound to this engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the base class for models (like db.Model in Flask)
Base = declarative_base()

# Custom db object to use with db.Model
class db:
    Model = Base
    engine = engine
    SessionLocal = SessionLocal
