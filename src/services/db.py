import json
from enum import Enum
from pathlib import Path
from typing import Type
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
    A mock NoSQL database service class that just stores documents on disk as JSON files.

    Notes
    -----
    - In production this could be replaced with Mongo DB, DocumentDB, Firestore, etc.
    """

    def __init__(self):
        self.db_dir = env.mock_nosql_db_dir

        for collection in Collection:
            collection_path = self.db_dir / collection.value
            if not collection_path.exists():
                collection_path.mkdir()

    def read(
            self,
            collection: Collection,
            document_id: str,
            output_class: Type[BaseModel],
    ) -> BaseModel | None:
        """
        Read document from database.
        """
        file_path = self._file_path(collection, document_id)

        if not file_path.exists():
            return None

        with open(file_path, 'r') as file:
            document = json.loads(file.read())

        document = output_class(**document)

        return document

    def create(
            self,
            collection: Collection,
            document: dict | BaseModel,
            document_id: str | None = None,
            overwrite: bool = False,
    ):
        """
        Create new document in database.
        """
        document_id = document_id or uuid4()
        file_path = self._file_path(collection, document_id)

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
        """
        Update existing document in database.
        """
        file_path = self._file_path(collection, document_id)

        if not file_path.exists():
            raise DatabaseException(f'Cannot update document as does not exist: {file_path}')

        return self.create(
            collection=collection,
            document=document,
            document_id=document_id,
            overwrite=True,
        )

    def _file_path(self, collection: Collection, document_id: str) -> Path:
        return self.db_dir / collection.value / f'{document_id}.json'
