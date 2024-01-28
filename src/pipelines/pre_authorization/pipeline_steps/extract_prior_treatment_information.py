from llama_index import VectorStoreIndex

from data_models.pre_authorization import PriorTreatmentInformation
from utils.prompt_utils import multiline_prompt


def extract_prior_treatment_information(index: VectorStoreIndex) -> PriorTreatmentInformation:
    """
    Determines whether prior conservative treatment was attempted and
    if so whether it was successful.

    Parameters
    ----------
    index: VectorStoreIndex
        An index of the medical record being queried.

    Returns
    -------
    WasConservativeTreatmentAttempted
    """
    query_engine = index.as_query_engine(
        output_cls=PriorTreatmentInformation,
    )

    prompt = multiline_prompt(
        """
        Read the medical report above which was sent to an American healthcare insurer for them to perform a Prior Authorization for a requested treatment.
        
        Has a conservative treatment already been attempted for the health issue in question prior to this request for treatment and if so, was it successful?

        Give your answer in JSON format with the following fields:
        - was_treatment_attempted
        - evidence_treatment_was_attempted
        - was_treatment_successful
        - evidence_treatment_was_successful
        
        Where:
         - The "was_treatment_attempted" field should be true if conservative treatment was attempted.
         - The "evidence_of_whether_treatment_was_attempted" should contain a short excerpt from the medical report that mentions whether treatment has already been attempted, or null if there is no mention of prior treatment.
         - The "was_treatment_successful" field should be true if conservative treatment was attempted and successful, or false if treament was attempted but unsuccessful or null if the report does not state whether the treatment was successful.
         - The "evidence_of_whether_treatment_was_successful" should contain a short excerpt from the medical report that mentions whether or not the attempted treatment was successful.
        """
    )

    response = query_engine.query(prompt)

    return response.response
