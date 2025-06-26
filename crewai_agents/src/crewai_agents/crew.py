#from crewai import Crew, Process
from crewai import Agent, Crew, Process, Task
from .setup import AgentFactory, TaskFactory

class AICrew:
    def __init__(self):
        self.agent_factory = AgentFactory()
        self.task_factory = TaskFactory()
    
    def create_thought_crew(self, input_data):
        # Create agents
        thought_simulator = self.agent_factory.create_agent('thought_simulator')
        thought_evaluator = self.agent_factory.create_agent('thought_evaluator')
        
        # Create tasks
        simulate_task = self.task_factory.create_task(
            'simulate_thoughts', thought_simulator, input_data)
        evaluate_task = self.task_factory.create_task(
            'evaluate_thoughts', thought_evaluator)
        
        # Set up crew
        return Crew(
            agents=[thought_simulator, thought_evaluator],
            tasks=[simulate_task, evaluate_task],
            process=Process.sequential,
            verbose=2
        )
    
    def create_council_crew(self, thought_process):
        # Create agents
        governance = self.agent_factory.create_agent('governance_agent')
        strategy = self.agent_factory.create_agent('strategy_agent')
        quality = self.agent_factory.create_agent('quality_agent')
        
        # Create tasks
        gov_task = self.task_factory.create_task(
            'governance_review', governance, thought_process)
        strat_task = self.task_factory.create_task(
            'strategy_review', strategy, thought_process)
        qual_task = self.task_factory.create_task(
            'quality_review', quality, thought_process)
        
        # Set up crew
        return Crew(
            agents=[governance, strategy, quality],
            tasks=[gov_task, strat_task, qual_task],
            process=Process.sequential,
            verbose=2
        )
    
    def create_correction_crew(self, original_output, issues):
        # Create agents
        detector = self.agent_factory.create_agent('drift_detector')
        adjuster = self.agent_factory.create_agent('prompt_adjuster')
        feedback = self.agent_factory.create_agent('feedback_injector')
        
        # Create tasks
        detect_task = self.task_factory.create_task(
            'detect_drift', detector, f"{original_output}\n\nIssues:{issues}")
        adjust_task = self.task_factory.create_task(
            'adjust_prompts', adjuster)
        feedback_task = self.task_factory.create_task(
            'inject_feedback', feedback)
        
        # Set up crew
        return Crew(
            agents=[detector, adjuster, feedback],
            tasks=[detect_task, adjust_task, feedback_task],
            process=Process.sequential,
            verbose=2
        )


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
