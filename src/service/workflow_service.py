import json
import logging

from src.config import TEAM_MEMBERS
from src.graph import build_graph, mix_agents_builder
from langchain_community.adapters.openai import convert_message_to_dict
import uuid

from src.graph.types import MixState
from langchain_core.messages import HumanMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Default level is INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def enable_debug_logging():
    """Enable debug level logging for more detailed execution information."""
    logging.getLogger("src").setLevel(logging.DEBUG)


logger = logging.getLogger(__name__)

# Create the graph
graph = build_graph()
mix_graph = mix_agents_builder()

# Cache for coordinator messages
coordinator_cache = []
MAX_CACHE_SIZE = 2


async def run_agent_workflow(
    user_input_messages: list,
    debug: bool = False,
    deep_thinking_mode: bool = False,
    search_before_planning: bool = False,
):
    """Run the agent workflow with the given user input.

    Args:
        user_input_messages: The user request messages
        debug: If True, enables debug level logging

    Returns:
        The final state after the workflow completes
    """
    if not user_input_messages:
        raise ValueError("Input could not be empty")

    if debug:
        enable_debug_logging()

    logger.info(f"Starting workflow with user input: {user_input_messages}")

    workflow_id = str(uuid.uuid4())

    streaming_llm_agents = [*TEAM_MEMBERS, "planner", "coordinator"]

    # Reset coordinator cache at the start of each workflow
    global coordinator_cache
    coordinator_cache = []
    global is_handoff_case
    is_handoff_case = False

    # TODO: extract message content from object, specifically for on_chat_model_stream
    async for event in graph.astream_events(
        {
            # Constants
            "TEAM_MEMBERS": TEAM_MEMBERS,
            # Runtime Variables
            "messages": user_input_messages,
            "deep_thinking_mode": deep_thinking_mode,
            "search_before_planning": search_before_planning,
        },
        version="v2",
    ):
        kind = event.get("event")
        data = event.get("data")
        name = event.get("name")
        metadata = event.get("metadata")
        node = (
            ""
            if (metadata.get("checkpoint_ns") is None)
            else metadata.get("checkpoint_ns").split(":")[0]
        )
        langgraph_step = (
            ""
            if (metadata.get("langgraph_step") is None)
            else str(metadata["langgraph_step"])
        )
        run_id = "" if (event.get("run_id") is None) else str(event["run_id"])

        if kind == "on_chain_start" and name in streaming_llm_agents:
            if name == "planner":
                yield {
                    "event": "start_of_workflow",
                    "data": {"workflow_id": workflow_id, "input": user_input_messages},
                }
            ydata = {
                "event": "start_of_agent",
                "data": {
                    "agent_name": name,
                    "agent_id": f"{workflow_id}_{name}_{langgraph_step}",
                },
            }
        elif kind == "on_chain_end" and name in streaming_llm_agents:
            ydata = {
                "event": "end_of_agent",
                "data": {
                    "agent_name": name,
                    "agent_id": f"{workflow_id}_{name}_{langgraph_step}",
                },
            }
        elif kind == "on_chat_model_start" and node in streaming_llm_agents:
            ydata = {
                "event": "start_of_llm",
                "data": {"agent_name": node},
            }
        elif kind == "on_chat_model_end" and node in streaming_llm_agents:
            ydata = {
                "event": "end_of_llm",
                "data": {"agent_name": node},
            }
        elif kind == "on_chat_model_stream" and node in streaming_llm_agents:
            content = data["chunk"].content
            if content is None or content == "":
                if not data["chunk"].additional_kwargs.get("reasoning_content"):
                    # Skip empty messages
                    continue
                ydata = {
                    "event": "message",
                    "data": {
                        "message_id": data["chunk"].id,
                        "delta": {
                            "reasoning_content": (
                                data["chunk"].additional_kwargs["reasoning_content"]
                            )
                        },
                    },
                }
            else:
                # Check if the message is from the coordinator
                if node == "coordinator":
                    if len(coordinator_cache) < MAX_CACHE_SIZE:
                        coordinator_cache.append(content)
                        cached_content = "".join(coordinator_cache)
                        if cached_content.startswith("handoff"):
                            is_handoff_case = True
                            continue
                        if len(coordinator_cache) < MAX_CACHE_SIZE:
                            continue
                        # Send the cached message
                        ydata = {
                            "event": "message",
                            "data": {
                                "message_id": data["chunk"].id,
                                "delta": {"content": cached_content},
                            },
                        }
                    elif not is_handoff_case:
                        # For other agents, send the message directly
                        ydata = {
                            "event": "message",
                            "data": {
                                "message_id": data["chunk"].id,
                                "delta": {"content": content},
                            },
                        }
                else:
                    # For other agents, send the message directly
                    ydata = {
                        "event": "message",
                        "data": {
                            "message_id": data["chunk"].id,
                            "delta": {"content": content},
                        },
                    }
        elif kind == "on_tool_start" and node in TEAM_MEMBERS:
            ydata = {
                "event": "tool_call",
                "data": {
                    "tool_call_id": f"{workflow_id}_{node}_{name}_{run_id}",
                    "tool_name": name,
                    "tool_input": data.get("input"),
                },
            }
        elif kind == "on_tool_end" and node in TEAM_MEMBERS:
            ydata = {
                "event": "tool_call_result",
                "data": {
                    "tool_call_id": f"{workflow_id}_{node}_{name}_{run_id}",
                    "tool_name": name,
                    "tool_result": data["output"].content if data.get("output") else "",
                },
            }
        else:
            continue
        yield ydata

    if is_handoff_case:
        yield {
            "event": "end_of_workflow",
            "data": {
                "workflow_id": workflow_id,
                "messages": [
                    convert_message_to_dict(msg)
                    for msg in data["output"].get("messages", [])
                ],
            },
        }

async def run_mix_agent_workflow(
    user_input_messages: list[dict],
    debug: bool = False,
    deep_thinking_mode: bool = False,
    search_before_planning: bool = False,
):
    if not user_input_messages:
        raise ValueError("Input could not be empty")

    if debug:
        logging.getLogger("src").setLevel(logging.DEBUG)

    messages = [HumanMessage(content=msg["content"]) for msg in user_input_messages]

    state = MixState(
        messages=messages,
        user_prompt=messages[-1].content,
        category="simple",  # reflector потом перезапишет правильную category
        answers=[],
        current_idx=0,
        results=[],
        deep_thinking_mode=deep_thinking_mode,
        search_before_planning=search_before_planning,
        agent_map={},
        task_blocks=[],
    )

    last_answers_count = 0
    seen_summary_started = False

    async for event in mix_graph.astream_events(state, version="v2"):
        kind = event.get("event")
        data = event.get("data", {})

        output = data.get("output", {})

        # 1) Ловим answers
        if hasattr(output, "update") and isinstance(output.update, dict) and "answers" in output.update:
            answers = output.update["answers"]
            if len(answers) > last_answers_count:
                last_answers_count = len(answers)
                yield {
                    "event": "answers",
                    "data": json.dumps([answers[-1]], ensure_ascii=False),
                }

        # 2) Стримим summary
        if kind == "on_chat_model_stream":
            seen_summary_started = True
            chunk = data.get("chunk")
            if chunk and chunk.content:
                yield {
                    "event": "message",
                    "data": json.dumps({
                        "message_id": chunk.id,
                        "delta": {"content": chunk.content},
                    }, ensure_ascii=False),
                }



    # 3) Страховка: если вдруг summary так и не пошёл
    if not seen_summary_started and last_answers_count > 0:
        yield {
            "event": "message",
            "data": json.dumps({
                "message_id": "final_summary",
                "delta": {"content": "\n\n".join(state["answers"])},
            }, ensure_ascii=False),
        }