
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    BigInteger,
)
from sqlalchemy.orm import relationship

from app.database import Base


class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), unique=True, nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    uploaded_by = Column(Integer, nullable=True, index=True)

    products = relationship(
        "Product",
        back_populates="image_file",
        foreign_keys="Product.image_file_id",
    )


class Product(Base):
    __tablename__ = "products"

    # Adapt these fields to your existing Product model.
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)

    image_file_id = Column(
        Integer,
        ForeignKey("file_metadata.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    image_file = relationship(
        "FileMetadata",
        back_populates="products",
        foreign_keys=[image_file_id],
    )
