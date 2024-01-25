from pathlib import Path

from env import env  # noqa
from pipelines.pre_authorization.pipeline_steps import (
    extract_requested_cpt_codes,
    extract_prior_treatment_information,
    create_cpt_guidelines_tree,
)

from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)

from utils.prompt_utils import multiline_prompt

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

    # 1) CONVERT CPT GUIDELINES TO DECISION TREE
    colonoscopy_guidelines = multiline_prompt(
        """
        1. Colorectal cancer screening, as indicated by 1 or more of the following:
            1.1 Patient has average-risk or higher, as indicated by ALL of the following
                1.1.1 Age 45 years or older
                1.1.2 No colonoscopy in past 10 years
            1.2 High risk family history, as indicated by 1 or more of the following:
                1.2.1 Colorectal cancer diagnosed in one or more first-degree relatives of any age and ALL of the following:
                    1.2.1.1 Age 40 years or older
                    1.2.1.2 Symptomatic (eg, abdominal pain, iron deficiency anemia, rectal bleeding)
                1.2.2 Family member with colonic adenomatous polyposis of unknown etiology
            1.3 Juvenile polyposis syndrome diagnosis indicated by 1 or more of the following:
                1.3.1 Age 12 years or older and symptomatic (eg, abdominal pain, iron deficiency anemia, rectal bleeding, telangiectasia)
                1.3.2 Age younger than 12 years and symptomatic (eg, abdominal pain, iron deficiency anemia, rectal bleeding, telangiectasia)
        """
    )
    cpt_guidelines_tree = create_cpt_guidelines_tree(colonoscopy_guidelines)

    # 2) EXTRACTING CPT CODE FROM MEDICAL RECORD
    cpt_codes = extract_requested_cpt_codes(index)
    print('Requested CPT Code(s): ', cpt_codes)

    # 3) DETERMINE WHETHER CONSERVATIVE TREATMENT WAS ATTEMPTED / SUCCESSFUL
    prior_treatment = extract_prior_treatment_information(index)
    print('Prior treatment attempted: ', prior_treatment.was_treatment_attempted)
    print('Evidence: ', prior_treatment.evidence_of_whether_treatment_was_attempted)
    print('Prior treatment successful: ', prior_treatment.was_treatment_successful)
    print('Evidence: ', prior_treatment.evidence_of_whether_treatment_was_successful)


