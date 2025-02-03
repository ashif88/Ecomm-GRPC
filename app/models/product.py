from sqlalchemy import Column, Integer, String, Float
from app.utils.db import db  # Import the custom db object

class Product(db.Model):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
