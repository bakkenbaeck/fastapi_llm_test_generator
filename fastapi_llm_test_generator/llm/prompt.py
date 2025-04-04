mock_prompt_template = """
Available mocks:
python ```
{code}
```

===
"""

fixtures_prompt_template = """
Available fixtures:
python ```
{code}
```

===
"""

pydantic_prompt_template = """
Pydantic models:
python```
{code}
```

===
"""

function_prompt_template = """
Functions:
python```
{code}
```

===
"""

db_prompt_template = """
Use these tables if necessary. Ids are usually autoincrement

{tables}

===
"""

code_prompt_template = """
Route to test:
python```
{code}
```
===
"""


pytest_prompt_template = """

{additional_prompt_pre}

Write tests(pytest) for the following fastapi route. 
Do not use mocks, use parameterize. If needed create a fixture to insert data. 
Include import statements when needed.

Url to use: {url}.

{additional_prompt_info}

{mock_prompt}

{fixtures_prompt}

{pydantic_prompt}

{function_prompt}

{db_prompt}

{code_prompt}

{additional_prompt_after}

"""
