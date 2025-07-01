from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type

class DelegateWorkToolInput(BaseModel):
    """Input schema for task delegation."""
    task: str = Field(..., description="Clear description of the task to delegate")
    context: str = Field(..., description="Relevant context for the task")
    expected_output: str = Field(..., description="What output is expected")

class DelegateWorkTool(BaseTool):
    name: str = "Delegate work to coworker"
    description: str = "Delegate a specific task to another agent with proper context"
    args_schema: Type[BaseModel] = DelegateWorkToolInput

    def _run(self, task: str, context: str, expected_output: str) -> str:
        # Implementation would connect to CrewAI's delegation system
        return f"Task delegated successfully:\nTask: {task}\nContext: {context}\nExpected Output: {expected_output}"


# from crewai.tools import BaseTool
# from typing import Type
# from pydantic import BaseModel, Field


# class MyCustomToolInput(BaseModel):
#     """Input schema for MyCustomTool."""
#     argument: str = Field(..., description="Description of the argument.")

# class MyCustomTool(BaseTool):
#     name: str = "Name of my tool"
#     description: str = (
#         "Clear description for what this tool is useful for, your agent will need this information to use it."
#     )
#     args_schema: Type[BaseModel] = MyCustomToolInput

#     def _run(self, argument: str) -> str:
#         # Implementation goes here
#         return "this is an example of a tool output, ignore it and move along."
