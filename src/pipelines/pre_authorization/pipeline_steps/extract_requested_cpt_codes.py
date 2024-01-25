from llama_index import VectorStoreIndex
from pydantic import BaseModel

from utils.prompt_utils import multiline_prompt


class CPTCodes(BaseModel):
    """Data model for extracted CPT codes."""
    cpt_codes: list[str]


def extract_requested_cpt_codes(index: VectorStoreIndex) -> list[str]:
    """
    Extracts the CPT code(s) for the requested procedures from the medical record.

    Parameters
    ----------
    index: VectorStoreIndex
        An index of the medical record being queried.

    Returns
    -------
    list[str]
        A list of the requested CPT codes.
    """
    query_engine = index.as_query_engine(
        output_cls=CPTCodes,
    )

    prompt = multiline_prompt(
        """
        Extract the CPT codes for the requested procedure(s) from this medical record.
    
        Each CPT code is a 5 digit number.
    
        Give the CPT code(s) only with no additional explanation or information.
        """
    )

    response = query_engine.query(prompt)

    return response.response.cpt_codes
