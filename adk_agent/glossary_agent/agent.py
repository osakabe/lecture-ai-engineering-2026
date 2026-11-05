from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from app import tools
from app.agent import INSTRUCTIONS
from app.config import MODEL

root_agent = Agent(
    model=MODEL,
    name="glossary_agent",
    instruction=INSTRUCTIONS,
    tools=[
        FunctionTool(
            tools.search_glossary,
            require_confirmation=True,
        ),
        tools.get_lecture_summary,
        tools.make_quiz,
    ],
)
