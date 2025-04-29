from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.runnables.base import Runnable
from typing import List

class MultiModelRunner(Runnable):
    """
    Runnable that queries multiple LLMs with the same prompt
    and merges their responses into a single AIMessage.
    """
    def __init__(self, models: List[BaseChatModel]):
        self.models = models

    def invoke(self, state, config=None):
        prompt_messages = state["messages"]
        parts: List[str] = []
        for model in self.models:
            resp = model.invoke(prompt_messages)
            parts.append(resp.content)
        combined = "\n\n---\n\n".join(parts)
        return AIMessage(content=combined)

    async def ainvoke(self, state, config=None):
        return self.invoke(state, config)
