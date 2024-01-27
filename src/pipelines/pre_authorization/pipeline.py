from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, field_serializer

from db_models.cpt_guidelines import CPTGuidelinesDocument
from pipelines.pre_authorization.pipeline_steps import (
    index_medical_record,
    extract_requested_cpt_codes,
    extract_prior_treatment_information,
    are_cpt_guideline_criteria_met,
)
from pipelines.pre_authorization.pipeline_steps.are_cpt_guideline_criteria_met import CriterionResult
from pipelines.pre_authorization.pipeline_steps.extract_prior_treatment_information import PriorTreatmentInformation
from services.db import Database, Collection
from utils.pydantic_utils import pretty_print_pydantic

logging.basicConfig(level=logging.INFO)


class ExitReason(Enum):
    PRIOR_TREATMENT_SUCCESSFUL = 'PRIOR_TREATMENT_SUCCESSFUL'
    GUIDELINE_CRITERIA_EVALUATED = 'GUIDELINE_CRITERIA_EVALUATED'


class PreAuthorizationPipelineResult(BaseModel):
    cpt_code: str
    exit_reason: ExitReason
    prior_treatment: PriorTreatmentInformation
    guidelines: str
    are_guideline_criteria_met: bool | None
    guideline_criteria_results: list[CriterionResult]

    @field_serializer('exit_reason')
    def serialize_exit_reason(self, exit_reason: ExitReason, *args):
        return exit_reason.value


def pre_authorization_pipeline(
        medical_record_file_path: str | Path,
        force_reindex: bool = False,
) -> PreAuthorizationPipelineResult:
    # 1) Load and index medical record for RAG pipeline.
    index = index_medical_record(
        medical_record_file_path=medical_record_file_path,
        force_reindex=force_reindex,
    )

    # 2) Extract requested CPT code(s) from medical record.
    cpt_codes = extract_requested_cpt_codes(index)
    if not cpt_codes:
        raise RuntimeError('Could not find any CPT codes in medical record')
    cpt_code = cpt_codes[0]  # todo handle case with >1 requested procedures.

    # 3) Load parsed CPT guidelines from database.
    db = Database()
    guidelines_document = db.read(
        collection=Collection.CPT_GUIDELINES,
        document_id=cpt_code,
        output_class=CPTGuidelinesDocument,
    )
    if not guidelines_document:
        raise RuntimeError(
            f"""
            Guidelines for requested CPT code {cpt_code} not available.
            You must run the CPT Guideline Ingestion pipeline on these guidelines first.
            """
        )

    # 4) Determine whether prior treatment was attempted and successful.
    prior_treatment = extract_prior_treatment_information(index)

    # 6) If prior treatment was successful, exist pipeline.
    if prior_treatment.was_treatment_attempted and prior_treatment.was_treatment_successful:
        return PreAuthorizationPipelineResult(
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

    return PreAuthorizationPipelineResult(
        cpt_code=cpt_code,
        exit_reason=ExitReason.GUIDELINE_CRITERIA_EVALUATED,
        prior_treatment=prior_treatment,
        guidelines=guidelines_document.guidelines,
        are_guideline_criteria_met=cpt_guideline_results.are_criteria_met,
        guideline_criteria_results=cpt_guideline_results.criteria_results,
    )


if __name__ == '__main__':
    file_path = input('Enter the file path for a medical record: ')
    file_path = Path(file_path)
    assert file_path.exists(), 'Medical record file does not exist'
    result = pre_authorization_pipeline(file_path)
    pretty_print_pydantic(result)
