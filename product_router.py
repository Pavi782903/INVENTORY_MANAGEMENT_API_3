
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_file_access
from app.schemas.product_schema import (
    ProductImageAssociation,
    ProductResponse,
)
from app.services.product_service import ProductService

router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products"],
)


@router.patch("/{product_id}/image", response_model=ProductResponse)
def associate_product_image(
    product_id: int,
    payload: ProductImageAssociation,
    db: Session = Depends(get_db),
    user: dict = Depends(require_file_access),
):
    return ProductService(db).associate_image(
        product_id=product_id,
        file_id=payload.file_id,
        user_id=user["id"],
    )


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(require_file_access),
):
    # This endpoint demonstrates the nested image metadata response.
    # Merge it with your existing product endpoint and permissions.
    return ProductService(db).get(product_id)
