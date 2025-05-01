from functools import lru_cache
from typing import Dict, List

from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_core.language_models import BaseChatModel 

from src.config.agents import LLM_ENDPOINTS, MODELS_BY_CAT

def _create_llm(cfg: Dict) -> BaseChatModel:
    kwargs = {"model": cfg["model"], "temperature": 0.0}
    prov = cfg.get("provider", "openai")

    if prov == "openai":
        if cfg.get("base_url"):
            kwargs["base_url"] = cfg["base_url"]
        if cfg.get("api_key"):
            kwargs["api_key"] = cfg["api_key"]
        return ChatOpenAI(**kwargs)

    elif prov == "deepseek":
        if cfg.get("base_url"):
            kwargs["api_base"] = cfg["base_url"]
        if cfg.get("api_key"):
            kwargs["api_key"] = cfg["api_key"]
        return ChatDeepSeek(**kwargs)

    else:
        raise ValueError(f"Unknown provider: {prov!r}")


@lru_cache(maxsize=None)
def get_llm(alias: str) -> BaseChatModel:
    if alias not in LLM_ENDPOINTS:
        raise KeyError(f"Alias {alias} not found in LLM_ENDPOINTS")
    return _create_llm(LLM_ENDPOINTS[alias])

def pick_llm(cat: str) -> List[BaseChatModel]:
    if cat not in MODELS_BY_CAT:
        raise KeyError(f"Category {cat!r} is not defined in MODELS_BY_CAT")
    return [get_llm(alias) for alias in MODELS_BY_CAT[cat]]

reflector_llm: BaseChatModel = get_llm("reflector_model")

thinking_llm: BaseChatModel = get_llm("thinking_model")

summary_llm:   BaseChatModel = get_llm("summary_model")
