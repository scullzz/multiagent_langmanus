from typing import Literal
from .env import BASIC_BASE_URL, BASIC_API_KEY
# Define available LLM types
LLMType = Literal["basic", "reasoning", "vision", "coding", 'business', 'web']

# Define agent-LLM mapping
AGENT_LLM_MAP: dict[str, LLMType] = {
    "coordinator": "basic",  # 协调默认使用basic llm
    "planner": "reasoning",  # 计划默认使用basic llm
    "supervisor": "basic",  # 决策使用basic llm
    "researcher": "basic",  # 简单搜索任务使用basic llm
    "coder": "coding",  # 编程任务使用basic llm
    "browser": "web",  # 浏览器操作使用vision llm
    "reporter": "basic",  # 编写报告使用basic llm
    "business": "business",  # 商务分析使用business llm
}

MODELS_BY_CAT: dict[str, list[str]] = {
    "simple":    ["mistral_small", "gpt4o_mini", "grok3_mini"],
    "complex":   ["gem_flash", "gpt4o_full", "grok3"],
    "coding":    ["gem_pro_T", "sonnet_T", "gpt4o_mini_high"],
    "reflector": ["reflector_model"], 
    "summary":   ["summary_model"], 
}

LLM_ENDPOINTS: dict[str, dict] = {
    # ------- simple -------
    "mistral_small":   {"model": "mistralai/mistral-small-3.1-24b-instruct",  "base_url": BASIC_BASE_URL, "api_key": BASIC_API_KEY},
    "gpt4o_mini":      {"model": "openai/o4-mini", "base_url": BASIC_BASE_URL, "api_key": BASIC_API_KEY},
    "grok3_mini":      {"model": "x-ai/grok-3-mini-beta", "base_url": BASIC_BASE_URL, "api_key": BASIC_API_KEY},
    # ------- complex ------
    "gem_flash":       {"model": "google/gemini-2.0-flash-001", "base_url": BASIC_BASE_URL, "api_key": BASIC_API_KEY},
    "gpt4o_full":      {"model": "openai/gpt-4o-search-preview", "base_url": BASIC_BASE_URL, "api_key": BASIC_API_KEY},
    "grok3":           {"model": "x-ai/grok-3-beta", "base_url": BASIC_BASE_URL, "api_key": BASIC_API_KEY},
    # ------- coding -------
    "gem_pro_T":       {"model": "google/gemini-2.5-pro-preview-03-25", "base_url": BASIC_BASE_URL, "api_key": BASIC_API_KEY},
    "sonnet_T":        {"model": "anthropic/claude-3.7-sonnet", "base_url": BASIC_BASE_URL, "api_key": BASIC_API_KEY},
    "gpt4o_mini_high": {"model": "openai/o4-mini-high", "base_url": BASIC_BASE_URL, "api_key": BASIC_API_KEY},
    # ------- reflector ----
    "reflector_model": {"model": "google/gemini-2.0-flash-001", "base_url": BASIC_BASE_URL, "api_key": BASIC_API_KEY},
    # ------- summary ------
    "summary_model":   {"model": "google/gemini-2.0-flash-001", "base_url": BASIC_BASE_URL, "api_key": BASIC_API_KEY},
}