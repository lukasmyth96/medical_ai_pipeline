from utils.prompt_utils import multiline_prompt


def test_multiline_prompt():
    """
    Test that the multiline_prompt function correctly strips leading and trailing
    spaces and tabs in a multiline prompt defines using a Python triple quote string.
    """
    prompt = """
    You are an AI.
    
    Do something cool.
    """

    cleaned_prompt = multiline_prompt(prompt)

    assert cleaned_prompt == 'You are an AI.\n\nDo something cool.'
