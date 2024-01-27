from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, field_serializer
from enum import Enum


class CPTGuidelinesDocument(BaseModel):
    file_path: str | Path
    cpt_code: str
    guidelines: str
    decision_tree: GuidelineDecisionTree


class GuidelineDecisionTree(BaseModel):
    """A nested tree representation of a set of CPT guidelines."""
    treatment: str
    criteria: list[Criterion]
    criteria_operator: LogicalOperator

    @field_serializer('criteria_operator')
    def serialize_operator(self, criteria_operator: LogicalOperator, *args):
        return criteria_operator.value if criteria_operator else None


class Criterion(BaseModel):
    criterion_id: str
    criterion: str
    criterion_question: str | None = None
    sub_criteria: list[Criterion]
    sub_criteria_operator: LogicalOperator | None = None

    @field_serializer('sub_criteria_operator')
    def serialize_operator(self, criteria_operator: LogicalOperator, *args):
        return criteria_operator.value if criteria_operator else None


class LogicalOperator(Enum):
    AND = 'AND'
    OR = 'OR'
    NONE = "NONE"
