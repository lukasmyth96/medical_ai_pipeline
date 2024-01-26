import logging

from llama_index import VectorStoreIndex
from pydantic import BaseModel

from pipelines.pre_authorization.pipeline_steps.create_cpt_guidelines_decision_tree import CPTGuidelineTree, Criterion, \
    LogicalOperator


class CriterionResult(BaseModel):
    criterion_id: str
    criterion: str
    is_criterion_met: bool


class CPTGuidelineResults(BaseModel):
    is_criteria_met: bool
    criteria_results: list[CriterionResult]


def are_cpt_guideline_criteria_met(
        cpt_guideline_tree: CPTGuidelineTree,
        index: VectorStoreIndex,
) -> CPTGuidelineResults:
    """
    Uses RAG query pipeline to query medical record to determine whether
    each individual criterion from the CPT guidelines is met and then
    combines these results logically to determine whether the criteria
    are met overall.

    Parameters
    ----------
    cpt_guideline_tree: CPTGuidelineTree
        A tree of the criteria from the CPT guidelines.
    index: VectorStoreIndex
        An index of the medical record being queried.

    Returns
    -------
    CPTGuidelineResults:
        Stores the overall result of whether the criteria are met
        as well as a breakdown of each individual criterion.
    """
    logging.info(f'Determining if CPT guideline criteria are met...')

    is_criteria_met, criteria_results = _evaluate_criteria(
        criteria=cpt_guideline_tree.criteria,
        operator=cpt_guideline_tree.criteria_operator,
    )

    logging.info(f'Successfully determined if CPT guideline criteria are met ✅')

    return CPTGuidelineResults(
        is_criteria_met=is_criteria_met,
        criteria_results=criteria_results,
    )


def _is_criterion_met(criterion: Criterion) -> CriterionResult:
    # Stub implementation. Replace with actual logic to determine if criterion is met
    is_met = True  # Placeholder logic
    return CriterionResult(
        criterion=criterion.criterion,
        criterion_id=criterion.criterion_id,
        is_criterion_met=is_met,
    )


def _evaluate_criteria(
        criteria: list[Criterion],
        operator: LogicalOperator,
) -> tuple[bool, list[CriterionResult]]:
    """
    Recursive function that traverses through tree of CPT guideline criteria,
    determines whether each individual criterion is met and then combines these
    results with the logical operators to determine whether the criteria as a
    whole are met.

    Parameters
    ----------
    criteria: list[Criterion]
        List of criteria.
    operator: LogicalOperator
        Whether the criteria results should be combined with an AND / OR operator.

    Returns
    -------
    tuple[bool, list[CriterionResult]]:
        - The bool indicates whether criteria as a whole are met.
        - The list[CriterionResult] stores the results from each individual criteria.
    """
    results: list[CriterionResult] = []
    if not criteria:
        return True, results

    final_result = (operator != LogicalOperator.OR)  # True for AND, False for OR
    for criterion in criteria:
        if criterion.sub_criteria:
            # Evaluate sub_criteria recursively
            sub_result, sub_results = _evaluate_criteria(
                criteria=criterion.sub_criteria,
                operator=criterion.sub_criteria_operator or LogicalOperator.NONE
            )
            results.append(
                CriterionResult(
                    criterion=criterion.criterion,
                    criterion_id=criterion.criterion_id,
                    is_criterion_met=sub_result,
                )
            )
            results.extend(sub_results)
            if operator == LogicalOperator.AND:
                final_result = final_result and sub_result
            elif operator == LogicalOperator.OR:
                final_result = final_result or sub_result
        else:
            # Evaluate leaf nodes
            criterion_result = _is_criterion_met(criterion)
            results.append(criterion_result)
            if operator == LogicalOperator.AND:
                final_result = final_result and criterion_result.is_criterion_met
            elif operator == LogicalOperator.OR:
                final_result = final_result or criterion_result.is_criterion_met

    return final_result, results
