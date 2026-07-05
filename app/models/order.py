from sqlalchemy import Column, ForeignKey, Integer

from app.utils.db import db  # Import the custom db object


class Order(db.Model):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
