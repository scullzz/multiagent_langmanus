from langgraph.graph import StateGraph
from .types import MixState
from src.graph.mix_nodes import reflector_node, simple_node, complex_node, coding_node, thinking_node, summary_node

def mix_agents_builder():
    graph = StateGraph(MixState)

    graph.add_node("reflector", reflector_node)
    graph.add_node("simple", simple_node)
    graph.add_node("complex", complex_node)
    graph.add_node("coding", coding_node)
    graph.add_node("thinking", thinking_node)
    graph.add_node("summary", summary_node)

    graph.set_entry_point("reflector")
    graph.add_edge("simple", "thinking")
    graph.add_edge("complex", "thinking")
    graph.add_edge("coding", "thinking")
    graph.set_finish_point("summary")

    return graph.compile()
