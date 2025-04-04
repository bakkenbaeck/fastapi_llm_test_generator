# FastAPI LLM Test Generator
---
*fastapi_llm_test_generator* is a tool that simplifies pytest creation for FastAPI projects leveraging LLMs. 


---
## Description

It automatically iterates over each FastAPI endpoint, analyzes the associated codebase for relevant context (including Pydantic models, function calls, and database tables), and uses a large language model to generate corresponding test functions. With this tool, you can quickly generate test cases tailored to your API endpoints, streamlining the testing process

# Disclaimer

This won't solve all your problems, yet. It generates tests based on your app context. It works best for simple enough use cases. Tests are there to test your application, make sure to read the generated tests and think about whether they make sense. Treat these as a starting point.

# Requirements

* fastapi app
* Anthropic API key



# Usage
Currently it best used from the command line. Inside your virtial env install the package e.g. via pip:

    pip install fastapi_llm_test_generator

make sure to install subdependencies:

    pip install fastapi_llm_test_generator[anthropic,psycopg2]

```console
$ python -m fastapi_llm_test_generator generate --help
20
                                                                                                                                                        
 Usage: python -m fastapi_llm_test_generator generate [OPTIONS]                                                                                         
                                                      SOURCE_APP_DIRECTORY                                                                              
                                                      CLIENT_PLUGIN                                                                                     
                                                      [TEST_DIRECTORY]                                                                                  
                                                                                                                                                        
╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    source_app_directory      PATH              Path to the FastAPI app directory [default: None] [required]                                        │
│ *    client_plugin             TEXT              Name of the AI client plugin to use [default: None] [required]                                      │
│      test_directory            [TEST_DIRECTORY]  Path to the tests app directory if none provided it will be create at source_app_directory/tests    │
│                                                  [default: tests]                                                                                    │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --config-file                                  PATH  Path to a config file [default: None]                                                           │
│ --db-plugin                                    TEXT  Optional database plugin to enable DB integration [default: None]                               │
│ --function-name                                TEXT  Target function name to generate tests for [default: None]                                      │
│ --route-path                                   TEXT  Filter routes matching this path or subpath [default: None]                                     │
│ --db-url                                       TEXT  Database URL used by the DB plugin [default: None]                                              │
│ --api-key                                      TEXT  API key for the selected AI client plugin [default: None]                                       │
│ --model                                        TEXT  LLM model name to use for test generation [default: None]                                       │
│ --additional-prompt-pre                        TEXT  Prompt text to prepend before the main content [default: None]                                  │
│ --additional-prompt-info                       TEXT  Prompt text to insert as additional context [default: None]                                     │
│ --mock-prompt                                  TEXT  Prompt describing mocks [default: None]                                                         │
│ --fixtures-prompt                              TEXT  Prompt describing fixtures [default: None]                                                      │
│ --additional-prompt-after                      TEXT  Prompt text to append after the main content [default: None]                                    │
│ --prompt-type                                  TEXT  Format/type of prompt to use (e.g., pytest) [default: pytest]                                   │
│ --overwrite                  --no-overwrite          Whether to overwrite existing tests, otherwise it will skip [default: no-overwrite]             │
│ --run-tests                  --no-run-tests          Run tests with pytest - this might fail due to insufficient config. Be carefule                 │
│                                                      [default: no-run-tests]                                                                         │
│ --help                                               Show this message and exit.                                                                     │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

As a convenience *fastapi_llm_test_generator* can readin a `config.json` to make sure reusable prompt parts can be inserted in multiple runs

```json
{
    "db_plugin": "psycopg2",
    "db_url": "postgresql://user:password@localhost:5432/database",
    "api_key": "some-key",
    "additional_prompt_pre": null,
    "additional_prompt_info": "Assume fixture 'database' using postgres and asyncpg (using $ syntax) for that. \n Use \"client\": httpx.AsyncClient \n* @pytest.mark.asyncio",
    "mock_prompt": null,
    "fixtures_prompt": "```python\n@pytest.fixture\nasync def login(database, app, client):\n    res = await client.post(\n        \"/api/v2/login\", data=dict(username=\"admin\", password=\"1234\", client_id=\"123\", grant_type=\"password\")\n    )\n    assert res.status_code == 200\n\n    name, val = res.headers[\"Set-Cookie\"].split(\"=\", maxsplit=1)\n    client.cookies[name] = val\n```",
    "additional_prompt_after": null,
    "prompt_type": "pytest"
  }
```

and then run `python -m fastapi_llm_test_generator generate . anthropic --config-file scripts/test_gen_config.json`

tests will be generated in a directory called `test` in your `source_app_directory` with subfolders resembling the api endpoints path.


# Future

* Run agent multiple times to make sure tests are correct
* Tests for this package :)
* openai support
* different databases