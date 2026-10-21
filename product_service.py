
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import FileMetadata
from app.repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)

    def associate_image(
        self, product_id: int, file_id: int, user_id: int
    ):
        product = self.repo.get(product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found.")

        metadata = (
            self.db.query(FileMetadata)
            .filter(FileMetadata.id == file_id)
            .first()
        )
        if metadata is None:
            raise HTTPException(status_code=404, detail="File not found.")

        if metadata.uploaded_by != user_id:
            raise HTTPException(
                status_code=403,
                detail="You cannot associate another user's file.",
            )

        if metadata.content_type not in ("image/jpeg", "image/png"):
            raise HTTPException(
                status_code=400,
                detail="Products can only use JPG or PNG images.",
            )

        # Only a reference is stored on the product.
        # The file itself remains in shared storage.
        try:
            self.repo.set_image(product, file_id)
            self.db.commit()
            self.db.refresh(product)
            return product
        except Exception:
            self.db.rollback()
            raise

    def get(self, product_id: int):
        product = self.repo.get(product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found.")
        return product
