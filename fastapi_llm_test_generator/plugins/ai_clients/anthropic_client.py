import logging
import re

from anthropic import Anthropic as Anthropic

from fastapi_llm_test_generator.llm.system import system_prompt
from fastapi_llm_test_generator.schemas import CodeResponse

from . import ai_clients_registry

logger = logging.getLogger(__name__)


class AnthropicClient:
    def __init__(self, ANTHROPIC_API_KEY: str, model: str = None):
        if ANTHROPIC_API_KEY is None or ANTHROPIC_API_KEY == "":
            raise Exception("Please provide an API KEY")

        self.client = Anthropic(
            api_key=ANTHROPIC_API_KEY,
        )

        if model is None:
            model = "claude-3-5-sonnet-latest"
        self.model = model

    def __call__(
        self, prompt: str, max_tokens: int = 2048, temperature: int = 0
    ) -> CodeResponse:
        message = self.client.messages.create(
            max_tokens=max_tokens,  # 1024,
            temperature=temperature,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}",
                },
            ],
            model=self.model,
        )

        text = message.content[0].text
        if "```python" in text:
            pattern = r"(?<=```python)(.*?)(?=```)"
            match = re.search(pattern, text, re.DOTALL)
            if match:
                text = match.group(0)

        logger.debug(f"AI Client response:\n {text}")

        return CodeResponse(
            content=text, tokens_used=message.usage.output_tokens, response=message
        )


@ai_clients_registry.register("anthropic")
def register_anthropic_client(ANTHROPIC_API_KEY: str, model: str = None):
    return AnthropicClient(ANTHROPIC_API_KEY=ANTHROPIC_API_KEY, model=model)
