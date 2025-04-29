from .env import (
    # Reasoning LLM
    REASONING_MODEL,
    REASONING_BASE_URL,
    REASONING_API_KEY,
    # Basic LLM
    BASIC_MODEL,
    BASIC_BASE_URL,
    BASIC_API_KEY,
    # Vision-language LLM
    VL_MODEL,
    VL_BASE_URL,
    VL_API_KEY,
    # Coding configuration LLM
    CODING_MODEL,
    CODING_BASE_URL,
    CODING_API_KEY,
    # Business configuration LLM
    BUSINESS_MODEL,
    BUSINESS_BASE_URL,
    BUSINESS_API_KEY,
    # Other configurations
    CHROME_INSTANCE_PATH,
)
from .tools import TAVILY_MAX_RESULTS

# Team configuration
TEAM_MEMBERS = ["dispatcher", "agent_runner",
                "researcher", "coder", "browser", "reporter"]


__all__ = [
    # Reasoning LLM
    "REASONING_MODEL",
    "REASONING_BASE_URL",
    "REASONING_API_KEY",
    # Basic LLM
    "BASIC_MODEL",
    "BASIC_BASE_URL",
    "BASIC_API_KEY",
    # Vision-language LLM
    "VL_MODEL",
    "VL_BASE_URL",
    "VL_API_KEY",
    # Other configurations
    "TEAM_MEMBERS",
    "TAVILY_MAX_RESULTS",
    "CHROME_INSTANCE_PATH",
    # Coding configuration LLM
    "CODING_MODEL",
    "CODING_BASE_URL",
    "CODING_API_KEY",
    # Business configuration LLM
    "BUSINESS_MODEL",
    "BUSINESS_BASE_URL",
    "BUSINESS_API_KEY",
]
