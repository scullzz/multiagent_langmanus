import json
import logging
import re
from typing import Literal

from langchain_core.messages import HumanMessage
from langgraph.types import Command
from src.agents.mix_agents import (
    coding_agent,
    complex_agent,
    simple_agent,
    reflector_agent,
    thinking_agent,
    summary_agent,
)
from src.prompts.template import apply_prompt_template

logger = logging.getLogger(__name__)

def clean_json_string(text: str) -> str:
    return re.sub(r"^```(?:json)?\s*([\s\S]*?)\s*```$", r"\1", text.strip())

def reflector_node(state: dict) -> Command[Literal["simple", "complex", "coding"]]:
    logger.info("▶ reflector_node started")

    user_message = state["messages"][-1].content

    messages = apply_prompt_template("reflector", {"messages": [HumanMessage(content=user_message)]})

    result = reflector_agent.invoke({"messages": messages})
    reply = result["messages"][-1].content

    cleaned_reply = clean_json_string(reply)

    try:
        category = json.loads(cleaned_reply)["category"]
    except Exception as e:
        raise ValueError(f"reflector_node: cannot parse category → {e}") from e

    goto = {
        "simple": "simple",
        "complex": "complex",
        "coding": "coding",
    }.get(category, "simple")

    return Command(
        update={
            "category": category,
            "user_prompt": user_message,
            "answers": [],
        },
        goto=goto,
    )


def simple_node(state: dict) -> Command[Literal["summary"]]:
    logger.info("▶ simple_node started")

    user_prompt = state["user_prompt"]
    messages = apply_prompt_template("simple_agent", {"messages": [HumanMessage(content=user_prompt)]})

    result = simple_agent.invoke({"messages": messages})

    answers = state.get("answers", [])
    answers.append(result.content)

    return Command(
        update={
            "answers": answers
        },
        goto="thinking",
    )

def complex_node(state: dict) -> Command[Literal["summary"]]:
    logger.info("▶ complex_node started")

    user_prompt = state["user_prompt"]
    messages = apply_prompt_template("complex_agent", {"messages": [HumanMessage(content=user_prompt)]})

    result = complex_agent.invoke({"messages": messages})

    answers = state.get("answers", [])
    answers.append(result.content)

    return Command(
        update={
            "answers": answers
        },
        goto="thinking",
    )

def coding_node(state: dict) -> Command[Literal["summary"]]:
    logger.info("▶ coding_node started")

    user_prompt = state["user_prompt"]
    messages = apply_prompt_template("coding_agent", {"messages": [HumanMessage(content=user_prompt)]})

    result = coding_agent.invoke({"messages": messages})

    answers = state.get("answers", [])
    answers.append(result.content)

    return Command(
        update={
            "answers": answers
        },
        goto="thinking",
    )

def thinking_node(state: dict) -> Command[Literal["summary"]]:
    logger.info("▶ thinking_node started")

    full_text = "\n\n".join(state.get("answers", []))

    result = thinking_agent.invoke({"messages": [HumanMessage(content=full_text)]})

    final_text = result["messages"][-1].content
    logger.info("Thinking agent produced final text: %s", final_text)

    new_history = state["messages"] + [HumanMessage(content=final_text)]

    return Command(
        update={
            "messages": new_history
        },
        goto="summary",
    )



def summary_node(state: dict) -> Command:
    logger.info("▶ summary_node started")
    logger.info("summary_node: state = %r", state)

    full_text = "\n\n".join(state["answers"])

    result = summary_agent.invoke({"messages": [HumanMessage(content=full_text)]})

    final_text = result["messages"][-1].content

    new_history = state["messages"] + [HumanMessage(content=final_text)]

    return Command(
        update={
            "messages": new_history
        },
        goto="end",
    )
