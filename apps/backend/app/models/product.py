"""
Domain models for Products and Product Categories.
Enables mapping procurement items to standard scopes.
"""

from typing import List, Optional
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class ProductCategory(Base, TimestampMixin):
    """
    High-level industrial or engineering category.
    E.g., 'Civil - Piping Systems', 'Electrical - Power Cables'.
    """
    __tablename__ = "product_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")


class Product(Base, TimestampMixin):
    """
    A commercial or engineering product targeted in tenders.
    E.g., 'High Density Polyethylene (HDPE) Pipes'.
    """
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("product_categories.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(256), index=True, nullable=False)
    aliases_csv: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    primary_standard_number: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationships
    category: Mapped[Optional["ProductCategory"]] = relationship("ProductCategory", back_populates="products")
