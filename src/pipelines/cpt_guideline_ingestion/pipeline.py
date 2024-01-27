from pathlib import Path

from db_models.cpt_guidelines import CPTGuidelinesDocument
from services.db import Database, Collection
from pipelines.cpt_guideline_ingestion.pipeline_steps import (
    parse_cpt_guidelines_from_pdf,
    create_guideline_decision_tree,
)


def cpt_guideline_ingestion_pipeline(cpt_guideline_file_path: str | Path) -> str:
    """
    Parses guidelines and CPT code from file, creates decision tree for
    guidelines and stores both in a document in the DB.

    Parameters
    ----------
    cpt_guideline_file_path: str | Path
        File path for a PDF file containing guidelines for a single CPT code.

    Returns
    -------
    str:
        The ID of the created DB document.
    """
    cpt_code = '45378'  # todo parse from PDF
    cpt_guidelines = parse_cpt_guidelines_from_pdf(cpt_guideline_file_path)
    cpt_guideline_decision_tree = create_guideline_decision_tree(cpt_guidelines)

    document = CPTGuidelinesDocument(
        file_path=str(cpt_guideline_file_path),
        cpt_code=cpt_code,
        guidelines=cpt_guidelines,
        decision_tree=cpt_guideline_decision_tree,
    )

    db = Database()

    document_id = db.create(
        collection=Collection.CPT_GUIDELINES,
        document=document,
        document_id=cpt_code,
    )

    return document_id


if __name__ == '__main__':

    file_path = input('Enter the file path for a CPT guidelines: ')
    file_path = Path(file_path)
    assert file_path.exists()
    cpt_guideline_ingestion_pipeline(file_path)
