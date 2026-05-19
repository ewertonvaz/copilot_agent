"""
This is the main entry point for the agent.
It defines the workflow graph, state, tools, nodes and edges.
"""

from typing_extensions import Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.types import Command
from langgraph.prebuilt import ToolNode
from copilotkit import CopilotKitState
from sample_agent.settings import settings


class AgentState(CopilotKitState):
    proverbs: list[str] = []
    language: Literal["english", "portuguese"] = "english"


@tool
def get_weather(location: str):
    """Get the weather for a given location."""
    return f"The weather for {location} is 70 degrees."


@tool
def get_image_url(filename: str = "logo_acAI_icone_transparente_300dpi.png"):
    """
    Get the full URL path to the company logo image file.

    Args:
        filename: The name of the image file. Defaults to logo_acAI_icone_transparente_300dpi.png

    Returns:
        The full URL path to the image file
    """
    return f"http://localhost:{settings.port}/images/{filename}"


tools = [get_weather, get_image_url]

# Shared model instance — created once per process, not per request
_model = ChatOpenAI(model="gpt-4o", api_key=settings.openai_api_key)


async def chat_node(state: AgentState, config: RunnableConfig) -> Command[Literal["tool_node", "__end__"]]:
    """
    Standard chat node based on the ReAct design pattern. It handles:
    - The model to use (and binds in CopilotKit actions and the tools defined above)
    - The system prompt
    - Getting a response from the model
    - Handling tool calls

    For more about the ReAct design pattern, see:
    https://www.perplexity.ai/search/react-agents-NcXLQhreS0WDzpVaS4m9Cg
    """
    model_with_tools = _model.bind_tools(
        [
            *state["copilotkit"]["actions"],
            get_weather,
            get_image_url,
        ],
        # Disabled to avoid race conditions; enable for faster parallel tool execution.
        parallel_tool_calls=False,
    )

    system_message = SystemMessage(
        content=f"""You are a helpful assistant. Talk in {state.get('language', 'english')}.

        If you need to show or generate any image, use the get_image_url tool.
        """
    )

    response = await model_with_tools.ainvoke([
        system_message,
        *state["messages"],
    ], config)

    if isinstance(response, AIMessage) and response.tool_calls:
        actions = state["copilotkit"]["actions"]
        if not any(
            action.get("name") == response.tool_calls[0].get("name")
            for action in actions
        ):
            return Command(goto="tool_node", update={"messages": response})

    return Command(goto=END, update={"messages": response})


workflow = StateGraph(AgentState)
workflow.add_node("chat_node", chat_node)
workflow.add_node("tool_node", ToolNode(tools=tools))
workflow.add_edge("tool_node", "chat_node")
workflow.set_entry_point("chat_node")
