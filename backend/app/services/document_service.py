from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.services.document_validation_service import validate_document
from app.services.extraction_service import extract_text

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploads"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


class DocumentService:

    def __init__(self, db: Session):
        self.repository = DocumentRepository(db)

    async def upload(
        self,
        file: UploadFile,
        owner_id,
    ) -> Document:

        validate_document(file)

        extension = Path(file.filename).suffix

        stored_filename = f"{uuid4()}{extension}"

        storage_path = UPLOAD_DIR / stored_filename

        content = await file.read()

        if len(content) > 10 * 1024 * 1024:
            raise ValueError("FILE_TOO_LARGE")

        # 1. Save file FIRST
        storage_path.write_bytes(content)

        print("Saved file:", storage_path)
        print("File exists:", storage_path.exists())

        # 2. THEN extract text
        try:
            extracted_text, page_count = extract_text(
                str(storage_path)
            )

            status = "READY"
        except Exception as exc:
            print("Extraction failed:", exc)

            extracted_text = None
            page_count = None
            status = "FAILED"

        document = Document(
            owner_id=owner_id,
            filename=stored_filename,
            original_filename=file.filename,
            mime_type=file.content_type,
            file_size=len(content),
            storage_path=str(storage_path),
            extracted_text=extracted_text,
            page_count=page_count,
            processing_status=status,
        )

        return self.repository.create(document)