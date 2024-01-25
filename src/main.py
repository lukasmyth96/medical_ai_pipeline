from pathlib import Path

from env import env  # noqa

from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

DATA_DIR = Path("/Users/lukasmyth/PycharmProjects/medical_ai_pipeline/data")

STORAGE_DIR = Path("/Users/lukasmyth/PycharmProjects/medical_ai_pipeline/database/llama_index_storage")


if __name__ == '__main__':

    documents = SimpleDirectoryReader(
        input_files=[
            DATA_DIR / 'medical-record-1.pdf'
        ],
        filename_as_id=True,
    ).load_data()

    if not STORAGE_DIR.exists():
        # load the documents and create the index
        index = VectorStoreIndex.from_documents(documents)
        # store it for later
        index.storage_context.persist(persist_dir=STORAGE_DIR)
    else:
        # load the existing index
        storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
        index = load_index_from_storage(storage_context)
        refreshed_docs = index.refresh_ref_docs(documents)

    # either way we can now query the index
    query_engine = index.as_query_engine()
    response = query_engine.query("What is the patient's name?")
    print(response)
