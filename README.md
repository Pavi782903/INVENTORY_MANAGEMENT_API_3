# Inventory Management and Document API

## Overview

A FastAPI application for securely uploading, storing, downloading, and managing JPG, PNG, and PDF files. File metadata is stored in MySQL using SQLAlchemy. Alembic manages database schema migrations.

## Requirements

- Python 3.10+
- MySQL
- MySQL Workbench (optional)
- Git

## Installation

1. Create and activate a virtual environment:

   ```bat
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install packages:

   ```bat
   python -m pip install -r requirements.txt
   ```

3. Create a MySQL database:

   ```sql
   CREATE DATABASE inventory_db;
   ```

4. Configure `.env`:

   ```dotenv
   DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/inventory_db
   JWT_SECRET_KEY=your_long_random_secret
   JWT_ALGORITHM=HS256
   UPLOAD_DIR=uploads
   MAX_FILE_SIZE=5242880
   ```

   Use the same JWT signing configuration as the existing authentication API.

5. Review the Alembic migration and apply it:

   ```bat
   alembic upgrade head
   ```

6. Start the server:

   ```bat
   uvicorn app.main:app --reload
   ```

7. Open Swagger UI:

   http://127.0.0.1:8000/docs

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/files/upload` | Upload a document |
| GET | `/api/v1/files` | List your file metadata |
| GET | `/api/v1/files/{file_id}` | Retrieve metadata |
| GET | `/api/v1/files/{file_id}/download` | Download a file |
| DELETE | `/api/v1/files/{file_id}` | Delete a file |
| PATCH | `/api/v1/products/{product_id}/image` | Associate an image |
| GET | `/api/v1/products/{product_id}` | Retrieve product and image metadata |

## Uploading a file

Use multipart/form-data with:

- `file`: The selected JPG, PNG, or PDF.
- `category`: `products` or `suppliers`.

The maximum file size is 5 MB. Empty files, unsupported extensions, mismatched content types, and invalid signatures are rejected.

## JWT authentication

The protected routes require an HTTP Bearer access token. In Swagger, click **Authorize** and enter the access token in the Bearer field. The example dependency expects a numeric user ID in the JWT `sub` claim.

Connect the existing Day 15 JWT and RBAC dependencies before deploying.

## Product image association

Send a PATCH request to `/api/v1/products/{product_id}/image` with JSON:

```json
{
  "file_id": 1
}
```

The file must belong to the authenticated user and be a JPG or PNG.

## Testing

Run validation tests:

```bat
python -m pytest tests -v
```

Also test upload, download, metadata retrieval, deletion, ownership checks, and product image association through Swagger or Postman.

## Security notes

- Uploaded content is stored on disk, not in the database.
- UUID-based filenames prevent collisions.
- File signatures are checked in addition to extension and MIME type.
- Uploaded files are not exposed as public static URLs.
- Keep `.env` and uploaded test documents out of Git.
- Production deployments should use malware scanning, request limits, HTTPS, and explicit RBAC policies.

## Notes on integration

Preserve existing Product, Category, Supplier, and User model fields. Add the image reference to the existing Product model and integrate the file routes with the current authentication and authorization implementation.
