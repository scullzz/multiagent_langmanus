from langgraph.graph import StateGraph
from .types import MixState
from src.graph.mix_nodes import reflector_node, simple_node, complex_node, coding_node, summary_node

def mix_agents_builder():
    graph = StateGraph(MixState)

    # Регистрируем все ноды
    graph.add_node("reflector", reflector_node)
    graph.add_node("simple", simple_node)
    graph.add_node("complex", complex_node)
    graph.add_node("coding", coding_node)
    graph.add_node("summary", summary_node)

    # Стартовая точка
    graph.set_entry_point("reflector")

    # ➡️ Переходы вручную: 
    # Reflector будет сразу решать, куда идти: в simple / complex / coding
    graph.add_edge("simple", "summary")
    graph.add_edge("complex", "summary")
    graph.add_edge("coding", "summary")

    # Финишная точка
    graph.set_finish_point("summary")

    return graph.compile()
