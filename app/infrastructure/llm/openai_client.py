from openai import OpenAI

from app.infrastructure.config.settings import settings
from app.infrastructure.llm.llm_port import LLMPort


class OpenAIClient(LLMPort):
    def __init__(self, model: str = "gpt-5-mini"):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = model

    def generate(self, prompt: str, system_message: str = "") -> str:
        instructions = system_message if system_message else None

        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=prompt,
        )

        return response.output_text
