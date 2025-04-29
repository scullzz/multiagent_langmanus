import logging, json, re, uuid
from copy import deepcopy
from typing import Literal

from langchain_core.messages import HumanMessage
from langgraph.types import Command
from langgraph.graph import END

from src.agents import research_agent, coder_agent, business_agent, browser_agent
from src.agents.llm import get_llm_by_type
from src.config.agents import AGENT_LLM_MAP
from langchain_core.messages import SystemMessage
from src.prompts.template import apply_prompt_template
from .types import State
import uuid, json, logging

logger = logging.getLogger(__name__)

RESPONSE_FORMAT = (
    "Response from {}:\n\n<response>\n{}\n</response>\n\n*Please execute the next step.*"
)

def _classify(text: str) -> Literal["research", "coder", "browser"]:
    t = text.lower()
    if any(k in t for k in ("код", "python", "script", "алгоритм", "code", "программа")):
        return "coder"
    if any(k in t for k in ("сайт", "url", "page", "найди")):
        return "browser"
    return "research"


def dispatcher_node(state: State) -> Command[Literal["agent_runner"]]:
    prompt = state["messages"][-1].content

    messages = apply_prompt_template("dispatcher", {"messages":[HumanMessage(content=prompt)]})

    llm = get_llm_by_type(AGENT_LLM_MAP["researcher"])
    reply = llm.invoke(messages).content

    blocks = json.loads(reply)
    task_blocks = [{"id": str(i), "text": b["text"]} for i, b in enumerate(blocks)]
    agent_map   = {str(i): b["agent"] for i, b in enumerate(blocks)}

    return Command(
        update={"task_blocks": task_blocks,
                "agent_map": agent_map,
                "results": []},
        goto="agent_runner",
    )

def agent_runner_node(state: State) -> Command[Literal["reporter"]]:
    results = state["results"]
    for blk in state["task_blocks"]:
        agent = state["agent_map"][blk["id"]]
        sub_state = state | {"messages":[HumanMessage(content=blk["text"])]}
        if agent == "research":
            res = research_node(sub_state)
        elif agent == "coder":
            res = code_node(sub_state)
        elif agent == "business":
            res = business_node(sub_state)
        elif agent == "browser":
            res = browser_node(sub_state)
        else:
            res = browser_node(sub_state)
        results.append({
            "block": blk,
            "agent": agent,
            "result": res.update["messages"][0].content,
        })
    return Command(goto="reporter")

def reporter_node(state: State) -> Command[Literal[END]]:
    logger.info("Reporter compiling final report")

    summary = "# Итоговая сводка\n\n"
    for r in state["results"]:
        summary += f"### {r['agent']}\n{r['result']}\n\n"

    short_state = {
        "messages": state["messages"] + [HumanMessage(content=summary, name="summarizer")]
    }

    messages = apply_prompt_template("reporter", short_state)

    response = get_llm_by_type(AGENT_LLM_MAP["reporter"]).invoke(messages)

    logger.info("Reporter finished task")
    logger.debug(f"Reporter response: {response.content}")

    state["messages"].append(
        HumanMessage(
            content=response.content,
            name="reporter",
        )
    )
    return Command(goto=END)

def research_node(state: State) -> Command[Literal["supervisor"]]:
    """Node for the researcher agent that performs research tasks."""
    logger.info("Research agent starting task")
    result = research_agent.invoke(state)
    logger.info("Research agent completed task")
    logger.debug(f"Research agent response: {result['messages'][-1].content}")
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format(
                        "researcher", result["messages"][-1].content
                    ),
                    name="researcher",
                )
            ]
        },
        goto="supervisor",
    )


def code_node(state: State) -> Command[Literal["dummy"]]:
    logger.info("Code agent starting task")
    result = coder_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content=RESPONSE_FORMAT.format(
                        "coder", result["messages"][-1].content
                    ),
                    name="coder",
                )
            ]
        },
        goto="dummy",
    )

def business_node(state: State) -> Command[Literal["dummy"]]:
    logger.info("Business agent starting task")
    result = business_agent.invoke(state)
    return Command(
        update={
            "messages": [HumanMessage(content=RESPONSE_FORMAT.format("business", result["messages"][-1].content), name="business")]
        },
        goto="dummy",
    )

def browser_node(state: State) -> Command[Literal["dummy"]]:
    logger.info("Browser (online) node started")

    answer_msg = browser_agent.invoke(state)

    return Command(
        update={
            "messages": [HumanMessage(content=RESPONSE_FORMAT.format("browser", answer_msg["messages"][-1].content), name="browser")]
        },
        goto="dummy",
    )