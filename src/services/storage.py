import json
from enum import Enum
from pathlib import Path
from typing import Type
from uuid import uuid4

from fastapi import File, UploadFile
from pydantic import BaseModel

from env import env


class Bucket(Enum):
    CPT_GUIDELINES = 'cpt_guidelines'


class DatabaseException(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class Storage:
    """
    A mock file storage service class that just stores files on disk.
    """

    def __init__(self):
        self.storage_dir = env.file_storage_dir

        for bucket in Bucket:
            bucket_dir = self.storage_dir / bucket.value
            if not bucket_dir.exists():
                bucket_dir.mkdir()

    def upload(self, file: UploadFile, bucket: Bucket):
        file_path = self.storage_dir / bucket.value / file.filename
        contents = file.file.read()
        with open(file_path, 'wb') as f:
            f.write(contents)

        return file_path