import re


def multiline_prompt(prompt: str) -> str:
    """
    Formats a multiline prompt written within Python triple quotes to
    remove any additional leading or trailing spaces and tabs.

    Parameters
    ----------
    prompt: str
        A multiline prompt.

    Returns
    -------
    str
        A cleaned multiline prompt.
    """

    # Remove duplicate spaces
    prompt = re.sub(r' +', ' ', prompt)

    # Remove duplicate tabs
    prompt = re.sub(r'\t+', '\t', prompt)

    # Remove duplicate newlines
    prompt = re.sub(r'\n+', '\n', prompt)

    # Remove leading and trailing spaces, tabs, and newlines
    prompt = prompt.strip()

    # Strip spaces after newline characters
    prompt = re.sub(r'\n\s', '\n', prompt)

    return prompt
