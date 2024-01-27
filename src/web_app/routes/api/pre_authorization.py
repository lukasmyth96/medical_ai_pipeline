from fastapi import APIRouter, UploadFile, File

from pipelines.pre_authorization.pipeline import pre_authorization_pipeline, PreAuthorizationPipelineResult
from services.storage import Storage, Bucket

router = APIRouter()


@router.post('/pre-authorization')
def pre_authorization_create(
        file: UploadFile = File(...),
) -> PreAuthorizationPipelineResult:

    storage = Storage()
    file_path = storage.upload(
        file=file,
        bucket=Bucket.MEDICAL_RECORDS,
    )

    result = pre_authorization_pipeline(
        medical_record_file_path=file_path
    )

    return result
