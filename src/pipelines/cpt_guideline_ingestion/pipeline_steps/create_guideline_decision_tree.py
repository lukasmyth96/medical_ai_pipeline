from __future__ import annotations

import logging

from llama_index.llms import OpenAI
from llama_index.program import OpenAIPydanticProgram

from data_models.cpt_guideline import GuidelineDecisionTree
from utils.prompt_utils import multiline_prompt


def create_guideline_decision_tree(cpt_guidelines: str) -> GuidelineDecisionTree:
    logging.info('Converting CPT guidelines into decision tree...')

    prompt_template_str = create_prompt()

    llm = OpenAI(
        model="gpt-3.5-turbo-0613",
        temperature=0.0,
    )

    program = OpenAIPydanticProgram.from_defaults(
        output_cls=GuidelineDecisionTree,
        prompt_template_str=prompt_template_str,
        llm=llm,
        verbose=False,
    )

    cpt_guidelines_tree = program(
        cpt_guidelines=cpt_guidelines
    )

    logging.info('Successfully converted CPT guidelines into decision tree ✅')

    return cpt_guidelines_tree


def create_prompt() -> str:
    return multiline_prompt(
        """
        I will provide you with a set of guidelines which are used by an American medical insurer during Prior Authorization to determine whether to approve a requested treatment.
        
        The guidelines will be formatted as a nested set of bullet points where each bullet point describes a single criterion and potentially a nested set of sub-criteria.
        
        I want you to convert the guidelines into a nested JSON tree structure where each object contains the following fields:
        - treatment: The name of the treatment in question.
        - criteria: A list of criteria for the treatment to be approved.
        - criteria_operator: A logic operator which determines whether any or all of the criteria must be met. The value should be "AND" if all criteria must be met or "OR" if any 1 criteria is sufficient.
        
        And each criteria object contains the following fields:
        - criterion: The criterion for a single bullet point.
        - criterion_question: A short yes or no question to determine whether this criterion is met. This field should only be populated for criteria that don't have sub-criteria.
        - criterion_id: The numeric ID of the bullet point in the format x.y.z.
        - sub_criteria: A (potentially empty) list of sub-criteria which are part of this criterion.
        - sub_criteria_operator: A logic operator which determines whether any or all of the sub-criteria must be met. The value should be "AND" if all criteria must be met or "OR" if any 1 criteria is sufficient.

        Example Input:
        1 Xray, as indicated by 1 or more of the following:
            1.1 Patient has average risk or higher, as indicated by ALL or the following:
                1.1.1 Age 60 or older.
                1.1.2 Fell on a hard surface.
            1.2 High risk family history, as indicated by 1 or more of the following:
                1.2.1 First-degree relative has brittle bone disease.
                1.2.2 Symptomatic (e.g. visible broken bone)
                
        Example Output:
        {{
            "treatment": "Xray",
            "criteria_operator": "OR"
            "criteria": [
                {{
                    "criterion": "Patient has average risk or higher",
                    "criterion_question": null,
                    "criterion_id": "1.1",
                    "sub_criteria_operator": "AND",
                    "sub_criteria": [
                        {{
                            "criterion": "Age 60 or older",
                            "criterion_question": "Is the patient 60 years old or older?",
                            "criterion_id": "1.1.1",
                            "sub_criteria": [],
                            "sub_criteria_operator": null
                        }},
                        {{
                            "criterion": "Fell on a hard surface.",
                            "criterion_question": "Did the patient fall on a hard surface?",
                            "criterion_id": "1.1.2",
                            "sub_criteria": [],
                            "sub_criteria_operator": null
                        }}
                    ]
                }},
                {{
                    "criterion": "High risk family history",
                    "criterion_id": "1.2"
                    "sub_criteria_operator": "OR",
                    "sub_criteria": [
                        {{
                            "criterion": "First-degree relative has brittle bone disease.",
                            "criterion_question": "Does the patient have a first-degree relative has brittle bone disease?",
                            "criterion_id": "1.2.1",
                            "sub_criteria": [],
                            "sub_criteria_operator": null
                        }},
                        {{
                            "criterion": "Symptomatic (e.g. visible broken bone)",
                            "criterion_question": "Is the patient symptomatic (e.g. visible broken bone)?",
                            "criterion_id": "1.2.2",
                            "sub_criteria": [],
                            "sub_criteria_operator": null
                        }}
                    ]
                }}
            ]
        }}
        
        Input:
        {cpt_guidelines}
        """
    )
