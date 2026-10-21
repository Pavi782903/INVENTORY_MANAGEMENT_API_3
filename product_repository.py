
from sqlalchemy.orm import Session

from app.models import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, product_id: int) -> Product | None:
        return (
            self.db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

    def set_image(self, product: Product, file_id: int) -> Product:
        product.image_file_id = file_id
        self.db.flush()
        return product
