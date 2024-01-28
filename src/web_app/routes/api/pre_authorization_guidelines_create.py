import re

from fastapi import APIRouter, UploadFile, File, HTTPException, Form

from data_models.cpt_guideline import CPTGuidelineDocument
from pipelines.cpt_guideline_ingestion.pipeline import cpt_guideline_ingestion_pipeline
from pipelines.exceptions import PipelineException
from services.db import Database, Collection
from services.storage import Storage, Bucket

router = APIRouter()


@router.post('/pre-authorization/guidelines')
def pre_authorization_guidelines_create(
        cpt_code: str = Form(...),
        guidelines_file: UploadFile = File(..., media_type='application/pdf'),
) -> CPTGuidelineDocument:
    """
    Extracts, parses and stores the guidelines for a single CPT code from a PDF.

    Notes
    -----
    - If the endpoint is called for a CPT code that has already
      been processed it will overwrite the existing DB document.

    Parameters
    ----------
    cpt_code: str
        The CPT code for which the guidelines are for.
    guidelines_file: UploadFile
        A PDF containing the guidelines for a single CPT code.

    Returns
    -------
    CPTGuidelineDocument:
        The generated DB document containing the parsed guidelines.
    """

    if guidelines_file.content_type != "application/pdf":
        raise HTTPException(400, detail="Invalid file type - must be PDF")

    if not _is_valid_cpt(cpt_code):
        raise HTTPException(400, detail="Invalid CPT code")

    storage = Storage()
    file_path = storage.upload(
        file=guidelines_file,
        bucket=Bucket.CPT_GUIDELINES,
    )

    try:
        guideline_document = cpt_guideline_ingestion_pipeline(
            cpt_guideline_file_path=file_path,
            cpt_code=cpt_code,
        )
    except PipelineException as exc:
        raise HTTPException(
            detail=exc.detail,
            status_code=exc.status_code,
        )

    Database().create(
        collection=Collection.CPT_GUIDELINES,
        document=guideline_document,
        document_id=cpt_code,
        overwrite=True,
    )

    return guideline_document


def _is_valid_cpt(cpt_code: str) -> bool:
    """
    Returns True if input is a valid CPT code.

    Parameters
    ----------
    cpt_code: str

    Returns
    -------
    bool:
        True if valid CPT code, else False.
    """
    # Regular expression for Category I (5 digits)
    category_1_pattern = re.compile(r'^\d{5}$')

    # Regular expression for Category II (4 digits followed by 'F')
    category_2_pattern = re.compile(r'^\d{4}F$')

    # Regular expression for Category III (4 digits followed by 'T')
    category_3_pattern = re.compile(r'^\d{4}T$')

    return category_1_pattern.match(cpt_code) or category_2_pattern.match(cpt_code) or category_3_pattern.match(cpt_code)
