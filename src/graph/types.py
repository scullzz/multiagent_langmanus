from typing import Literal, List, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph import MessagesState

from src.config import TEAM_MEMBERS

# routing
OPTIONS = TEAM_MEMBERS + ["FINISH"]


class Router(TypedDict):
    next: Literal[*OPTIONS]


class State(MessagesState):
    TEAM_MEMBERS: List[str]

    next: str
    full_plan: str
    deep_thinking_mode: bool
    search_before_planning: bool

    task_blocks: List[Dict[str, Any]]   # [{'id': str, 'text': str}, ...]
    agent_map: Dict[str, str]           # block_id → agent_name
    current_idx: int                    # индекс текущего блока
    results: List[Dict[str, Any]]       # накопленные ответы


class MixState(MessagesState):
    user_prompt: str
    category: Literal["simple", "complex", "coding"]
    answers: List[str]
    current_idx: int = 0  # Индекс текущего блока или задачи
    results: List[Dict[str, Any]] = []  # Накопленные ответы
    deep_thinking_mode: bool = False
    search_before_planning: bool = False
    agent_map: Dict[str, str] = {}
    task_blocks: List[Dict[str, Any]] = []  # [{'id': str, 'text': str}, ...]
