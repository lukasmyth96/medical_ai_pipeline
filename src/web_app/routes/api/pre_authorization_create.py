from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException

from pipelines.exceptions import PipelineException
from pipelines.pre_authorization.pipeline import pre_authorization_pipeline, PreAuthorizationDocument
from services.db import Database, Collection
from services.storage import Storage, Bucket

router = APIRouter()


@router.post('/pre-authorization')
def pre_authorization_create(
        medical_record_file: UploadFile = File(...),
) -> PreAuthorizationDocument:
    """
    Runs the pre-authorization pipeline for a single medical record,
    stores the result in the DB and then returns it.

    Notes
    -----
    - A 400 error will be returned if the guidelines for the requested
      CPT code(s) have not already been ingested by the 'cpt_guideline_ingestion'
      pipeline.

    Parameters
    ----------
    medical_record_file:
        A PDF containing the medical record which requests one or more
        medical procedures identified by their CPT codes.

    Returns
    -------
    PreAuthorizationDocument:
        The generated DB document containing the results of the Pre Authorization
        pipeline.
    """
    if medical_record_file.content_type != "application/pdf":
        raise HTTPException(400, detail="File must be a PDF")

    storage = Storage()
    file_path = storage.upload(
        file=medical_record_file,
        bucket=Bucket.MEDICAL_RECORDS,
    )

    try:
        pre_authorization_document = pre_authorization_pipeline(
            medical_record_file_path=file_path
        )
    except PipelineException as exc:
        raise HTTPException(
            detail=exc.detail,
            status_code=exc.status_code,
        )

    Database().create(
        collection=Collection.PRE_AUTHORIZATIONS,
        document=pre_authorization_document,
        document_id=uuid4(),
        overwrite=False,
    )

    return pre_authorization_document
