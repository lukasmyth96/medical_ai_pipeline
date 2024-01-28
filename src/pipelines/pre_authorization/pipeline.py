from __future__ import annotations

import logging
from pathlib import Path

from data_models.cpt_guideline import CPTGuidelineDocument
from data_models.pre_authorization import PreAuthorizationDocument, ExitReason
from pipelines.exceptions import PipelineException
from pipelines.pre_authorization.pipeline_steps import (
    index_medical_record,
    extract_requested_cpt_codes,
    extract_prior_treatment_information,
    are_cpt_guideline_criteria_met,
)

from services.db import Database, Collection
from utils.pydantic_utils import pretty_print_pydantic

logging.basicConfig(level=logging.INFO)


def pre_authorization_pipeline(
        medical_record_file_path: str | Path,
        force_reindex: bool = False,
) -> PreAuthorizationDocument:
    # 1) Load and index medical record for RAG pipeline.
    index = index_medical_record(
        medical_record_file_path=medical_record_file_path,
        force_reindex=force_reindex,
    )

    # 2) Extract requested CPT code(s) from medical record.
    cpt_codes = extract_requested_cpt_codes(index)
    if not cpt_codes:
        raise PipelineException(
            'Could not find any CPT codes in medical record'
        )
    cpt_code = cpt_codes[0]  # todo handle case with >1 requested procedures.

    # 3) Load parsed CPT guidelines from database.
    db = Database()
    guidelines_document = db.read(
        collection=Collection.CPT_GUIDELINES,
        document_id=cpt_code,
        output_class=CPTGuidelineDocument,
    )
    if not guidelines_document:
        raise PipelineException(
            f"""
            Guidelines for requested CPT code {cpt_code} not available.
            You must run the CPT Guideline Ingestion pipeline on these guidelines first.
            """
        )

    # 4) Determine whether prior treatment was attempted and successful.
    prior_treatment = extract_prior_treatment_information(index)

    # 6) If prior treatment was successful, exist pipeline.
    if prior_treatment.was_treatment_attempted and prior_treatment.was_treatment_successful:
        return PreAuthorizationDocument(
            cpt_code=cpt_code,
            exit_reason=ExitReason.PRIOR_TREATMENT_SUCCESSFUL,
            prior_treatment=prior_treatment,
            guidelines=guidelines_document.guidelines,
            are_guideline_criteria_met=None,
            guideline_criteria_results=[],
        )

    # 7 Determine whether CPT guideline criteria are met.
    cpt_guideline_results = are_cpt_guideline_criteria_met(
        cpt_guideline_tree=guidelines_document.decision_tree,
        index=index,
    )

    return PreAuthorizationDocument(
        cpt_code=cpt_code,
        exit_reason=ExitReason.GUIDELINE_CRITERIA_EVALUATED,
        prior_treatment=prior_treatment,
        guidelines=guidelines_document.guidelines,
        are_guideline_criteria_met=cpt_guideline_results.are_criteria_met,
        guideline_criteria_results=cpt_guideline_results.criteria_results,
    )


if __name__ == '__main__':
    """Script for testing."""
    logging.basicConfig(level=logging.INFO)
    file_path = input('Enter the file path for a medical record: ')
    file_path = Path(file_path)
    assert file_path.exists(), 'Medical record file does not exist'
    result = pre_authorization_pipeline(file_path)
    pretty_print_pydantic(result)
