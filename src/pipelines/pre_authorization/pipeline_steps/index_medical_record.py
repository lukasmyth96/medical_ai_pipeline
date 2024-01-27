import shutil
from pathlib import Path

from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

from env import env


def index_medical_record(
        medical_record_file_path: str | Path,
        force_reindex: bool = False,
) -> VectorStoreIndex:
    """
    Loads and indexes medical record for RAG pipeline using LlamaIndex.

    Notes
    -----
    - The created index will be saved to disk to avoid re-indexing the same document.
    - The index will be loaded from disk if this document has already been indexed.

    Parameters
    ----------
    medical_record_file_path: str | Path
        File path for a single medical record.
    force_reindex: bool
        Whether to force a reindex if this document has already been indexed.

    Returns
    -------
    VectorStoreIndex
        LlamaIndex index which can be used for RAG.
    """

    vector_db_index_dir = env.vector_db_dir / medical_record_file_path.name.rstrip('.pdf')

    if vector_db_index_dir.exists() and force_reindex:
        shutil.rmtree(str(vector_db_index_dir))

    documents = SimpleDirectoryReader(
        input_files=[medical_record_file_path],
        filename_as_id=True,
    ).load_data()

    if not vector_db_index_dir.exists():
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=vector_db_index_dir)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=vector_db_index_dir)
        index = load_index_from_storage(storage_context)
        index.refresh_ref_docs(documents)

    return index
