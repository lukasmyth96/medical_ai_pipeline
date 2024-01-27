import json
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel

from env import env


class Collection(Enum):
    CPT_GUIDELINES = 'cpt_guidelines'


class DatabaseException(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class Database:
    """
    A mock database service class that just stores data on disk as JSON files.
    """

    def __init__(self):
        self.db_dir = env.mock_nosql_db_dir

        for collection in Collection:
            collection_path = self.db_dir / collection.value
            if not collection_path.exists():
                collection_path.mkdir()

    def create(
            self,
            collection: Collection,
            document: dict | BaseModel,
            document_id: str | None = None,
            overwrite: bool = False,
    ):
        document_id = document_id or uuid4()
        file_path = self.db_dir / collection.value / f'{document_id}.json'

        if file_path.exists() and not overwrite:
            raise DatabaseException(f'Document already exists: {file_path}')

        if isinstance(document, BaseModel):
            document = document.model_dump()

        with open(file_path, 'w') as file:
            file.write(json.dumps(document, indent=4))

        return document_id

    def update(
            self,
            collection: Collection,
            document: dict | BaseModel,
            document_id: str,
    ):

        file_path = self.db_dir / collection.value / f'{document_id}.json'

        if not file_path.exists():
            raise DatabaseException(f'Cannot update document as does not exist: {file_path}')

        return self.create(
            collection=collection,
            document=document,
            document_id=document_id,
            overwrite=True,
        )
