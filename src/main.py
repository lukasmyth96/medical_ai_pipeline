from pathlib import Path

from env import env  # noqa
from pipelines.pre_authorization.pipeline_steps import extract_requested_cpt_codes

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
            DATA_DIR / 'medical-record-3.pdf'
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

    cpt_codes = extract_requested_cpt_codes(index)

    print('CPT Code(s): ', cpt_codes)
