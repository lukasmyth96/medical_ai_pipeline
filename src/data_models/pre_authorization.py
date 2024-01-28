from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_serializer


class ExitReason(Enum):
    PRIOR_TREATMENT_SUCCESSFUL = 'PRIOR_TREATMENT_SUCCESSFUL'
    GUIDELINE_CRITERIA_EVALUATED = 'GUIDELINE_CRITERIA_EVALUATED'


class PriorTreatmentInformation(BaseModel):
    """Data model for the response of the query to determine
    whether conservative treatment was attempted and successful."""
    was_treatment_attempted: bool
    evidence_of_whether_treatment_was_attempted: Optional[str]

    was_treatment_successful: Optional[bool]
    evidence_of_whether_treatment_was_successful: Optional[str]


class CriterionResult(BaseModel):
    criterion_id: str
    criterion: str
    criterion_question: str | None = None
    is_criterion_met: bool | None = None
    reason: str
    evidence: str | None = None
    information_required: str | None = None


class CPTGuidelineResults(BaseModel):
    are_criteria_met: bool
    criteria_results: list[CriterionResult]


class PreAuthorizationDocument(BaseModel):
    """
    Data model for a document in the 'pre_authorizations' DB collection.
    """
    cpt_code: str
    exit_reason: ExitReason
    prior_treatment: PriorTreatmentInformation
    guidelines: str
    are_guideline_criteria_met: bool | None
    guideline_criteria_results: list[CriterionResult]

    @field_serializer('exit_reason')
    def serialize_exit_reason(self, exit_reason: ExitReason, *args):
        return exit_reason.value
