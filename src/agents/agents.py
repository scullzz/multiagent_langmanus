from langgraph.prebuilt import create_react_agent

from src.prompts import apply_prompt_template
from src.tools import (
    bash_tool,
    crawl_tool,
    python_repl_tool,
    tavily_tool,
)

from .llm import get_llm_by_type
from src.config.agents import AGENT_LLM_MAP

research_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["researcher"]),
    tools=[tavily_tool, crawl_tool],
    prompt=lambda state: apply_prompt_template("researcher", state),
)

coder_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["coder"]),
    tools=[python_repl_tool, bash_tool],
    prompt=lambda state: apply_prompt_template("coder", state),
)

browser_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["browser"]),
    tools=[],
    prompt=lambda state: apply_prompt_template("browser", state),
)

business_agent = create_react_agent(
    get_llm_by_type(AGENT_LLM_MAP["business"]),
    tools=[tavily_tool],
    prompt=lambda state: apply_prompt_template("business", state),
)