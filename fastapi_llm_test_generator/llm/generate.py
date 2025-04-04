from .prompt import (
    code_prompt_template,
    db_prompt_template,
    fixtures_prompt_template,
    function_prompt_template,
    mock_prompt_template,
    pydantic_prompt_template,
    pytest_prompt_template,
)


def make_prompt(
    additional_prompt_pre: str = None,
    additional_prompt_info: str = None,
    mock_prompt: str = None,
    fixtures_prompt: str = None,
    url: str = None,
    pydantic_prompt: str = None,
    function_prompt: str = None,
    db_prompt: str = None,
    code_prompt: str = None,
    additional_prompt_after: str = None,
    prompt_type: str = "pytest",
):
    if prompt_type == "pytest":
        prompt = pytest_prompt_template.format(
            additional_prompt_pre=additional_prompt_pre
            if additional_prompt_pre
            else "",
            additional_prompt_info=additional_prompt_info
            if additional_prompt_info
            else "",
            mock_prompt=mock_prompt_template.format(code=mock_prompt)
            if mock_prompt
            else "",
            fixtures_prompt=fixtures_prompt_template.format(code=fixtures_prompt)
            if fixtures_prompt
            else "",
            url=url if url else "",
            pydantic_prompt=pydantic_prompt_template.format(code=pydantic_prompt)
            if pydantic_prompt
            else "",
            function_prompt=function_prompt_template.format(code=function_prompt)
            if function_prompt
            else "",
            db_prompt=db_prompt_template.format(tables=db_prompt) if db_prompt else "",
            code_prompt=code_prompt_template.format(code=code_prompt)
            if code_prompt
            else "",
            additional_prompt_after=additional_prompt_after
            if additional_prompt_after
            else "",
        )
    else:
        raise Exception(f"prompt_type: {prompt_type} not supported")

    return prompt
