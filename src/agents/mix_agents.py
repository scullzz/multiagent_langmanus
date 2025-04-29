from langgraph.prebuilt import create_react_agent
from src.prompts import apply_prompt_template
from src.agents.mix_lim import pick_llm, reflector_llm, summary_llm
from .mix_multi_runner import MultiModelRunner
from langchain_core.runnables import RunnableLambda

simple_agent = RunnableLambda(
    lambda st: {"messages": apply_prompt_template("simple_agent", st)}
) | MultiModelRunner(pick_llm("simple"))

complex_agent = RunnableLambda(
    lambda st: {"messages": apply_prompt_template("complex_agent", st)}
) | MultiModelRunner(pick_llm("complex"))

coding_agent = RunnableLambda(
    lambda st: {"messages": apply_prompt_template("coding_agent", st)}
) | MultiModelRunner(pick_llm("coding"))



reflector_agent = create_react_agent(
    reflector_llm,
    tools=[],
    prompt=lambda st: apply_prompt_template("reflector", st),
)

summary_agent = create_react_agent(
    summary_llm,
    tools=[],
    prompt=lambda st: apply_prompt_template("summary", st),
)
