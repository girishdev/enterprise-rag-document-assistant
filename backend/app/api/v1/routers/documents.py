from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.document import DocumentRead
from app.services.document_service import DocumentService
from uuid import UUID



router = APIRouter()


@router.post(
    "",
    response_model=DocumentRead,
)
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    service = DocumentService(db)

    try:
        return await service.upload(
            file=file,
            owner_id=current_user.id,
        )

    except ValueError as exc:
        if str(exc) == "INVALID_FILE_TYPE":
            raise HTTPException(
                status_code=400,
                detail="Only PDF, DOCX and TXT files are allowed",
            )

        if str(exc) == "FILE_TOO_LARGE":
            raise HTTPException(
                status_code=400,
                detail="Maximum file size is 10 MB",
            )

        raise


@router.get(
    "",
    response_model=list[DocumentRead],
)
def list_documents(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    service = DocumentService(db)

    return service.repository.list_by_owner(
        current_user.id
    )


@router.get(
    "/{document_id}",
    response_model=DocumentRead,
)
def get_document(
    document_id: UUID,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    service = DocumentService(db)

    document = service.repository.get_by_id(
        document_id
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    if document.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    return document


@router.delete(
    "/{document_id}",
)
def delete_document(
    document_id: UUID,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    service = DocumentService(db)

    document = service.repository.get_by_id(
        document_id
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    if document.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    service.repository.delete(document)

    return {
        "message": "Document deleted successfully"
    }