from typing import Dict, Any, List
import yaml
from pathlib import Path
from crewai import Agent, Task, Crew
from crewai.tools import Tool
from tools.safety_tools import SAFETY_TOOLS
from config.settings import settings

class ConstitutionalCrew:
    def __init__(self):
        self.agents_config = self._load_config("agents.yaml")
        self.tasks_config = self._load_config("tasks.yaml")
        self.agents = self._create_agents()
        self.tasks = self._create_tasks()
        self.crew = self._assemble_crew()
    
    def _load_config(self, filename: str) -> Dict[str, Any]:
        with open(Path(__file__).parent.parent / "config" / filename) as f:
            return yaml.safe_load(f)
    
    def _create_agents(self) -> Dict[str, Agent]:
        agents = {}
        
        for agent_name, config in self.agents_config.items():
            tools = []
            for tool_name in config.get("tools", []):
                if tool_name in SAFETY_TOOLS:
                    tool = SAFETY_TOOLS[tool_name]
                    tools.append(Tool(
                        name=tool.name,
                        func=tool.run,
                        description=tool.description
                    ))
            
            agents[agent_name] = Agent(
                role=config["role"],
                goal=config["goal"],
                backstory=config["backstory"],
                tools=tools,
                verbose=config.get("verbose", False),
                max_iter=config.get("max_iter", 3)
            )
        
        return agents
    
    def _create_tasks(self) -> Dict[str, Task]:
        tasks = {}
        
        for task_name, config in self.tasks_config.items():
            agent = self.agents.get(config.get("agent", ""))
            if not agent:
                continue
                
            tasks[task_name] = Task(
                description=config["description"],
                agent=agent,
                expected_output=config["expected_output"],
                tools=[Tool(
                    name=tool.name,
                    func=tool.run,
                    description=tool.description
                ) for tool in agent.tools],
                async_execution=config.get("async_execution", False),
                context=[tasks[ctx] for ctx in config.get("context", []) if ctx in tasks]
            )
        
        return tasks
    
    def _assemble_crew(self) -> Crew:
        return Crew(
            agents=list(self.agents.values()),
            tasks=list(self.tasks.values()),
            verbose=2,
            full_output=True
        )
    
    def validate_response(self, response: str) -> Dict[str, Any]:
        """Validate a response through the constitutional crew"""
        inputs = {"response": response}
        result = self.crew.kickoff(inputs=inputs)
        
        # Parse the full output to get individual task results
        validation_results = {}
        for task in self.tasks.values():
            if task.agent.name in result.actions:
                validation_results[task.agent.name] = {
                    "status": "APPROVED" if "APPROVED" in result.actions[task.agent.name].output else "REJECTED",
                    "output": result.actions[task.agent.name].output
                }
        
        # Determine final approval
        all_approved = all(
            result["status"] == "APPROVED" 
            for result in validation_results.values()
        )
        
        return {
            "final_response": result.output if all_approved else None,
            "validation_results": validation_results,
            "is_approved": all_approved
        }

# Singleton instance
constitutional_crew = ConstitutionalCrew()


# from crewai import Agent, Crew, Process, Task
# from crewai.project import CrewBase, agent, crew, task
# from crewai.agents.agent_builder.base_agent import BaseAgent
# from typing import List
# # If you want to run a snippet of code before or after the crew starts,
# # you can use the @before_kickoff and @after_kickoff decorators
# # https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

# @CrewBase
# class CrewaiAgents():
#     """CrewaiAgents crew"""

#     agents: List[BaseAgent]
#     tasks: List[Task]

#     # Learn more about YAML configuration files here:
#     # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
#     # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
#     # If you would like to add tools to your agents, you can learn more about it here:
#     # https://docs.crewai.com/concepts/agents#agent-tools
#     @agent
#     def researcher(self) -> Agent:
#         return Agent(
#             config=self.agents_config['researcher'], # type: ignore[index]
#             verbose=True
#         )

#     @agent
#     def reporting_analyst(self) -> Agent:
#         return Agent(
#             config=self.agents_config['reporting_analyst'], # type: ignore[index]
#             verbose=True
#         )

#     # To learn more about structured task outputs,
#     # task dependencies, and task callbacks, check out the documentation:
#     # https://docs.crewai.com/concepts/tasks#overview-of-a-task
#     @task
#     def research_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['research_task'], # type: ignore[index]
#         )

#     @task
#     def reporting_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['reporting_task'], # type: ignore[index]
#             output_file='report.md'
#         )

#     @crew
#     def crew(self) -> Crew:
#         """Creates the CrewaiAgents crew"""
#         # To learn how to add knowledge sources to your crew, check out the documentation:
#         # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

#         return Crew(
#             agents=self.agents, # Automatically created by the @agent decorator
#             tasks=self.tasks, # Automatically created by the @task decorator
#             process=Process.sequential,
#             verbose=True,
#             # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
#         )
