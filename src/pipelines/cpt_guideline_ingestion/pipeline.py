import logging
from pathlib import Path

from db_models.cpt_guidelines import CPTGuidelinesDocument
from services.db import Database, Collection
from pipelines.cpt_guideline_ingestion.pipeline_steps import (
    parse_cpt_guidelines_from_pdf,
    create_guideline_decision_tree,
)
from utils.pydantic_utils import pretty_print_pydantic


def cpt_guideline_ingestion_pipeline(
        cpt_guideline_file_path: str | Path,
        cpt_code: str,
        overwrite: bool = False,
) -> CPTGuidelinesDocument:
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
    db = Database()

    existing_document = db.read(
        collection=Collection.CPT_GUIDELINES,
        document_id=cpt_code,
        output_class=CPTGuidelinesDocument
    )

    if existing_document and not overwrite:
        raise RuntimeError(
            f"""
            Guidelines for CPT code {cpt_code} have already been ingested.
            Pass "overwrite=True" to the pipeline to overwrite them.
            """
        )

    cpt_guidelines = parse_cpt_guidelines_from_pdf(cpt_guideline_file_path)
    cpt_guideline_decision_tree = create_guideline_decision_tree(cpt_guidelines)

    document = CPTGuidelinesDocument(
        file_path=str(cpt_guideline_file_path),
        cpt_code=cpt_code,
        guidelines=cpt_guidelines,
        decision_tree=cpt_guideline_decision_tree,
    )

    document_id = db.create(
        collection=Collection.CPT_GUIDELINES,
        document=document,
        document_id=cpt_code,
        overwrite=overwrite,
    )

    return document


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    file_path = input('Enter the file path for a CPT guidelines: ')
    cpt_code = input('Enter 5 digit CPT code: ')
    overwrite_if_exists = "y" in input("Do you want to overwrite if exists? (y/n): ").lower()
    file_path = Path(file_path)
    assert file_path.exists(), 'Guideline file does not exist'
    document = cpt_guideline_ingestion_pipeline(
        cpt_guideline_file_path=file_path,
        cpt_code=cpt_code,
        overwrite=overwrite_if_exists,
    )
    pretty_print_pydantic(document)
