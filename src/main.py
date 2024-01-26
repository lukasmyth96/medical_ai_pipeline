from pathlib import Path
import logging

from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

from env import env  # noqa
from utils.pydantic_utils import pretty_print_pydantic
from pipelines.pre_authorization.pipeline_steps import (
    extract_requested_cpt_codes,
    extract_prior_treatment_information,
    parse_cpt_guidelines_from_pdf,
    create_cpt_guidelines_tree,
    are_cpt_guideline_criteria_met,
)

logging.basicConfig(level=logging.INFO)

DATA_DIR = Path("/Users/lukasmyth/PycharmProjects/medical_ai_pipeline/data")

STORAGE_ROOT_DIR = Path("/Users/lukasmyth/PycharmProjects/medical_ai_pipeline/database/llama_index_storage")


if __name__ == '__main__':

    filename = 'medical-record-1.pdf'

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

    # PARSE AND FORMAT CPT GUIDELINES FROM PDF
    colonoscopy_guidelines = parse_cpt_guidelines_from_pdf(DATA_DIR / 'colonoscopy-guidelines.pdf')

    # CONVERT CPT GUIDELINES TO DECISION TREE
    cpt_guidelines_tree = create_cpt_guidelines_tree(colonoscopy_guidelines)

    # DETERMINE IF CPT GUIDELINES CRITERIA ARE MET
    cpt_guideline_results = are_cpt_guideline_criteria_met(
        cpt_guideline_tree=cpt_guidelines_tree,
        index=index,
    )

    # EXTRACTING CPT CODE FROM MEDICAL RECORD
    cpt_codes = extract_requested_cpt_codes(index)
    print('Requested CPT Code(s): ', cpt_codes)

    # DETERMINE WHETHER CONSERVATIVE TREATMENT WAS ATTEMPTED / SUCCESSFUL
    prior_treatment = extract_prior_treatment_information(index)
    print('Prior treatment attempted: ', prior_treatment.was_treatment_attempted)
    print('Evidence: ', prior_treatment.evidence_of_whether_treatment_was_attempted)
    print('Prior treatment successful: ', prior_treatment.was_treatment_successful)
    print('Evidence: ', prior_treatment.evidence_of_whether_treatment_was_successful)
