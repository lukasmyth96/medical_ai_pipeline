from pathlib import Path

from pypdf import PdfReader

from openai import OpenAI

from utils.prompt_utils import multiline_prompt


def parse_cpt_guidelines_from_pdf(pdf_file_path: str | Path):
    """
    Parses CPT guidelines from the first page of the given PDF, removes additional
    text and enumerates and formats bullet points for easier processing later
    in the pipeline.

    Parameters
    ----------
    pdf_file_path: str | Path
        The file path of PDF containing the CPT guidelines.

    Returns
    -------
    cpt_guidelines: str
        The formatted, enumerated CPT guidelines.

    Examples
    --------
    The returned bullet points will be formatted as follows:
    ```
        1. ...
            1.1 ...
                1.1.1 ...
                1.1.2 ...
            1.2 ...
    ```
    """
    reader = PdfReader(str(pdf_file_path))

    cpt_guidelines = reader.pages[0].extract_text()

    cpt_guidelines = _strip_text_preceding_first_bullet_point(cpt_guidelines)

    cpt_guidelines = _convert_to_enumerated_bullet_points(cpt_guidelines)

    return cpt_guidelines


def _convert_to_enumerated_bullet_points(cpt_guidelines: str) -> str:
    """
    Calls GPT to convert raw CPT guidelines into well formatted, enumerated bullet points.

    Notes
    -----
    - This transformation will make it easier to parse the guidelines
      into a more logical data structure in the next step of the pipeline.
    - The numbers in the bullet points will serve as IDs for each criterion.

    Parameters
    ----------
    cpt_guidelines: str
        The raw CPT guidelines parsed from the PDF.

    Returns
    -------
    str:
        The enumerated bullet points

    Examples
    --------
    The returned bullet points will be formatted as follows:
    ```
        1. ...
            1.1 ...
                1.1.1 ...
                1.1.2 ...
            1.2 ...
    ```
    """

    system_prompt = multiline_prompt(
        """
        I will send you blocks of raw text which has been parsed from a PDF.
        
        The text will contain a block of nested bullet points but they may not be formatted properly.
        
        Rewrite the bullet points such that they are enumerated.
        
        Ignore any text that comes before or after the block of bullet points.
        """
    )

    example1_input = multiline_prompt(
            """
            This document is private   \n12344 26th Jan, technology;  • Xray, as demonstrated by at least one of these: o Patient has high risk, as indicated by all or the following: § Aged over 60 years § Fell on hard surface o High risk in family history
            """
        )

    example1_output = multiline_prompt(
        """
        1. Xray, as demonstrated by at least one of these:
           1.1. Patient has high risk, as indicated by all of the following:
                1.1.1. Aged over 60 years
                1.1.2. Fell on hard surface
           1.2. High risk in family history
        """
    )

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": example1_input,
        },
        {
            "role": "assistant",
            "content": example1_output,
        },
        {
            "role": "user",
            "content": cpt_guidelines
        }
    ]

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0
    )

    cpt_guidelines = response.choices[0].message.content

    return cpt_guidelines


def _strip_text_preceding_first_bullet_point(cpt_guidelines: str) -> str:
    bullet_pos = cpt_guidelines.find('•')
    if bullet_pos != -1:
        return cpt_guidelines[bullet_pos:]
    else:
        return cpt_guidelines
