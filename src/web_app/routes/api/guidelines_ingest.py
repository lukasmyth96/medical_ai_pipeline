from fastapi import APIRouter, UploadFile, File

from db_models.cpt_guidelines import CPTGuidelinesDocument
from pipelines.cpt_guideline_ingestion.pipeline import cpt_guideline_ingestion_pipeline
from services.storage import Storage, Bucket

router = APIRouter()


@router.post('/pre-authorization/guidelines')
def pre_authorization_guidelines_ingest(
        cpt_code: str,
        file: UploadFile = File(...),
) -> CPTGuidelinesDocument:

    storage = Storage()
    file_path = storage.upload(
        file=file,
        bucket=Bucket.CPT_GUIDELINES,
    )

    document = cpt_guideline_ingestion_pipeline(
        cpt_guideline_file_path=file_path,
        cpt_code=cpt_code,
        overwrite=True,
    )

    return document
