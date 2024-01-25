from pathlib import Path

from env import env  # noqa
from pipelines.pre_authorization.pipeline_steps import (
    extract_requested_cpt_codes,
    extract_prior_treatment_information,
)

from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

DATA_DIR = Path("/Users/lukasmyth/PycharmProjects/medical_ai_pipeline/data")

STORAGE_ROOT_DIR = Path("/Users/lukasmyth/PycharmProjects/medical_ai_pipeline/database/llama_index_storage")


if __name__ == '__main__':

    filename = 'medical-record-3.pdf'

    documents = SimpleDirectoryReader(
        input_files=[
            DATA_DIR / filename
        ],
        filename_as_id=True,
    ).load_data()

    storage_dir = STORAGE_ROOT_DIR / filename.rstrip('.pdf')

    if not storage_dir.exists():
        # load the documents and create the index
        index = VectorStoreIndex.from_documents(documents)
        # store it for later
        index.storage_context.persist(persist_dir=storage_dir)
    else:
        # load the existing index
        storage_context = StorageContext.from_defaults(persist_dir=storage_dir)
        index = load_index_from_storage(storage_context)
        refreshed_docs = index.refresh_ref_docs(documents)

    cpt_codes = extract_requested_cpt_codes(index)
    print('Requested CPT Code(s): ', cpt_codes)

    prior_treatment = extract_prior_treatment_information(index)
    print('Prior treatment attempted: ', prior_treatment.was_treatment_attempted)
    print('Evidence: ', prior_treatment.evidence_of_whether_treatment_was_attempted)
    print('Prior treatment successful: ', prior_treatment.was_treatment_successful)
    print('Evidence: ', prior_treatment.evidence_of_whether_treatment_was_successful)
