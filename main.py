
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import Base
from app.routers.file_router import router as file_router
from app.routers.product_router import router as product_router
from app.services.file_service import prepare_storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    prepare_storage()
    yield


app = FastAPI(
    title="Inventory Management and Document API",
    description="Inventory products, secure file uploads, and downloads.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(file_router)
app.include_router(product_router)


@app.get("/", tags=["Health"])
def root():
    return {"message": "Inventory File API is running."}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
