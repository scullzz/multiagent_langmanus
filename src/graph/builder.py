from langgraph.graph import StateGraph, START, END
from .types import State
from .nodes import dispatcher_node, agent_runner_node, reporter_node

def build_graph():
    g = StateGraph(State)

    g.add_node("dispatcher", dispatcher_node)
    g.add_node("agent_runner", agent_runner_node)
    g.add_node("reporter", reporter_node)

    g.add_edge(START, "dispatcher")
    g.add_edge("dispatcher", "agent_runner")
    g.add_edge("agent_runner", "reporter")
    g.add_edge("reporter", END)

    g.set_entry_point("dispatcher")

    return g.compile()
