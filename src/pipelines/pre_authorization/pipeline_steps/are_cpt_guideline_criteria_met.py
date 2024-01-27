import logging
from datetime import datetime

from llama_index import VectorStoreIndex, ServiceContext
from llama_index.llms import OpenAI
from pydantic import BaseModel

from pipelines.cpt_guideline_ingestion.pipeline_steps.create_guideline_decision_tree import (
    Criterion,
    GuidelineDecisionTree,
    LogicalOperator,
)
from utils.prompt_utils import multiline_prompt


class CriterionResult(BaseModel):
    criterion_id: str
    criterion: str
    criterion_question: str | None = None
    is_criterion_met: bool | None = None
    reason: str
    evidence: str | None = None
    information_required: str | None = None


class CPTGuidelineResults(BaseModel):
    is_criteria_met: bool
    criteria_results: list[CriterionResult]


def are_cpt_guideline_criteria_met(
        cpt_guideline_tree: GuidelineDecisionTree,
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
    logging.info('Determining if CPT guideline criteria are met...')

    is_criteria_met, criteria_results = _evaluate_criteria(
        criteria=cpt_guideline_tree.criteria,
        operator=cpt_guideline_tree.criteria_operator,
        index=index,
    )

    logging.info('Successfully determined if CPT guideline criteria are met ✅')

    return CPTGuidelineResults(
        is_criteria_met=is_criteria_met,
        criteria_results=criteria_results,
    )


def _is_criterion_met(
        criterion: Criterion,
        index: VectorStoreIndex,
) -> CriterionResult:
    """
    Uses GPT to determine whether criterion is met and obtain evidence.

    Parameters
    ----------
    criterion

    Returns
    -------

    """
    if not criterion.criterion_question:
        raise RuntimeError(f'Criterion {criterion.criterion_id} in guidelines tree has no question')

    class QAResponse(BaseModel):
        """Data model containing the answer to the question and evidence for the answer."""
        answer: bool | None = None
        reason: str
        evidence: str | None = None
        additional_information_required: str | None = None

    prompt = multiline_prompt(
        f"""
        Read the medical report above which was sent to an American healthcare insurer for them to perform a Prior Authorization for a requested treatment and answer the question below:

        {criterion.criterion_question}
        
        For context (for any date and age related questions), today's is {datetime.now().strftime('%B %d, %Y"')}.
        
        Give your answer in JSON format with the following fields:
            - answer
            - reason
            - evidence
            - additional_information_required
            
        Where:
            - The "answer" field should be true if the answer to the question is yes, or false if the answer to the question is no, or null if the question cannot be answered from the report.
            - The "reason" field should contain a one sentence justification for the answer given that references which information (or lack of information) in the medical report was used to arrive at that answer.
            - The "evidence" field should contain a short excerpt from the medical report that acts as evidence for the answer, or null if the report contains no information that answers the question.
            - The "additional_information_required" should be populated only if the question cannot be answered from the information available and should contain a one-sentence explanation of what additional information is needed to answer the question.
        """
    )

    llm = OpenAI(
        model="gpt-3.5-turbo-0613",
        # model='gpt-4-1106-preview',
        temperature=0.0,
    )

    service_context = ServiceContext.from_defaults(llm=llm)

    query_engine = index.as_query_engine(
        output_cls=QAResponse,
        service_context=service_context,
    )

    response = query_engine.query(prompt)

    qa_response = response.response

    logging.info(f' - Criteria {criterion.criterion_id}) {criterion.criterion}: {"✅" if qa_response.answer else "❌" if qa_response.answer is False else "❓"}')

    return CriterionResult(
        criterion=criterion.criterion,
        criterion_question=criterion.criterion_question,
        criterion_id=criterion.criterion_id,
        is_criterion_met=qa_response.answer,
        reason=qa_response.reason,
        evidence=qa_response.evidence,
        information_required=qa_response.additional_information_required,
    )


def _evaluate_criteria(
        criteria: list[Criterion],
        operator: LogicalOperator,
        index: VectorStoreIndex,
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
                operator=criterion.sub_criteria_operator or LogicalOperator.NONE,
                index=index,
            )
            results.append(
                CriterionResult(
                    criterion=criterion.criterion,
                    criterion_id=criterion.criterion_id,
                    is_criterion_met=sub_result,
                    reason=f'Sub-criteria are{" not" if not sub_result else ""} met.'
                )
            )
            results.extend(sub_results)
            if operator == LogicalOperator.AND:
                final_result = final_result and sub_result
            elif operator == LogicalOperator.OR:
                final_result = final_result or sub_result
        else:
            # Evaluate leaf nodes
            criterion_result = _is_criterion_met(
                criterion=criterion,
                index=index,
            )
            results.append(criterion_result)
            if operator == LogicalOperator.AND:
                final_result = final_result and criterion_result.is_criterion_met
            elif operator == LogicalOperator.OR:
                final_result = final_result or criterion_result.is_criterion_met

    return final_result, results
