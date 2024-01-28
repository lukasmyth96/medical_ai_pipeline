import logging
from pathlib import Path

from data_models.cpt_guideline import CPTGuidelineDocument
from pipelines.cpt_guideline_ingestion.pipeline_steps import (
    parse_cpt_guidelines_from_pdf,
    create_guideline_decision_tree,
)
from utils.pydantic_utils import pretty_print_pydantic


def cpt_guideline_ingestion_pipeline(
        cpt_guideline_file_path: str | Path,
        cpt_code: str,
) -> CPTGuidelineDocument:
    """
    Parses guidelines from PDF and creates a logical decision tree.

    Parameters
    ----------
    cpt_guideline_file_path: str | Path
        File path for a PDF file containing guidelines for a single CPT code.
    cpt_code:
        The CPT code for which the guidelines are for.

    Returns
    -------
    str:
        The ID of the created DB document.
    """
    cpt_guidelines = parse_cpt_guidelines_from_pdf(cpt_guideline_file_path)
    cpt_guideline_decision_tree = create_guideline_decision_tree(cpt_guidelines)

    return CPTGuidelineDocument(
        file_path=str(cpt_guideline_file_path),
        cpt_code=cpt_code,
        guidelines=cpt_guidelines,
        decision_tree=cpt_guideline_decision_tree,
    )


if __name__ == '__main__':
    """Script for testing."""
    logging.basicConfig(level=logging.INFO)
    file_path = input('Enter the file path for a CPT guidelines: ')
    cpt_code = input('Enter 5 digit CPT code: ')
    file_path = Path(file_path)
    assert file_path.exists(), 'Guideline file does not exist'
    document = cpt_guideline_ingestion_pipeline(
        cpt_guideline_file_path=file_path,
        cpt_code=cpt_code,
    )
    pretty_print_pydantic(document)
