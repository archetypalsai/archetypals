from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import Dict, Any, List
from datetime import datetime
from .schemas import AlignmentReport, CouncilDecision

@CrewBase
class AICouncilCrew():
    """Orchestration crew for AI alignment and governance"""

    def __init__(self):
        self.manager_agent = Agent(
            role="Council Manager",
            goal="Coordinate the council's decision-making process",
            backstory="An experienced mediator who ensures all council members work together effectively",
            verbose=True,
            allow_delegation=False
        )

    @agent
    def thought_simulator(self) -> Agent:
        return Agent(
            config=self.agents_config['thought_simulator'],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def thought_evaluator(self) -> Agent:
        return Agent(
            config=self.agents_config['thought_evaluator'],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def governance_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['governance_agent'],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def strategy_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['strategy_agent'],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def quality_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['quality_agent'],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def drift_detector(self) -> Agent:
        return Agent(
            config=self.agents_config['drift_detector'],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def prompt_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['prompt_engineer'],
            verbose=True,
            allow_delegation=False
        )

    @task
    def simulate_thoughts(self) -> Task:
        return Task(
            config=self.tasks_config['simulate_thoughts'],
            output_file='thought_simulation.md',
            agent=self.thought_simulator()
        )

    @task
    def evaluate_alignment(self) -> Task:
        return Task(
            config=self.tasks_config['evaluate_alignment'],
            output_file='alignment_report.json',
            agent=self.thought_evaluator(),
            context=[self.simulate_thoughts()]
        )

    @task
    def governance_review(self) -> Task:
        return Task(
            config=self.tasks_config['governance_review'],
            output_file='governance_assessment.json',
            agent=self.governance_agent(),
            context=[self.evaluate_alignment()]
        )

    @task
    def strategy_review(self) -> Task:
        return Task(
            config=self.tasks_config['strategy_review'],
            output_file='strategy_assessment.json',
            agent=self.strategy_agent(),
            context=[self.evaluate_alignment()]
        )

    @task
    def quality_audit(self) -> Task:
        return Task(
            config=self.tasks_config['quality_audit'],
            output_file='quality_report.json',
            agent=self.quality_agent(),
            context=[
                self.governance_review(),
                self.strategy_review()
            ]
        )

    @task
    def detect_drift(self) -> Task:
        return Task(
            config=self.tasks_config['detect_drift'],
            output_file='drift_report.json',
            agent=self.drift_detector(),
            context=[self.quality_audit()]
        )

    @task
    def correct_prompts(self) -> Task:
        return Task(
            config=self.tasks_config['correct_prompts'],
            output_file='prompt_corrections.md',
            agent=self.prompt_engineer(),
            context=[self.detect_drift()]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the AI Governance Council crew"""
        return Crew(
            agents=[
                self.thought_simulator(),
                self.thought_evaluator(),
                self.governance_agent(),
                self.strategy_agent(),
                self.quality_agent(),
                self.drift_detector(),
                self.prompt_engineer()
            ],
            tasks=[
                self.simulate_thoughts(),
                self.evaluate_alignment(),
                self.governance_review(),
                self.strategy_review(),
                self.quality_audit(),
                self.detect_drift(),
                self.correct_prompts()
            ],
            process=Process.hierarchical,
            manager_agent=self.manager_agent,  # Using separate manager agent
            verbose=True,
            full_output=True,
            memory=True
        )



# #from crewai import Crew, Process
# from crewai import Agent, Crew, Process, Task
# from .setup import AgentFactory, TaskFactory

# class AICrew:
#     def __init__(self):
#         self.agent_factory = AgentFactory()
#         self.task_factory = TaskFactory()
    
#     def create_thought_crew(self, input_data):
#         # Create agents
#         thought_simulator = self.agent_factory.create_agent('thought_simulator')
#         thought_evaluator = self.agent_factory.create_agent('thought_evaluator')
        
#         # Create tasks
#         simulate_task = self.task_factory.create_task(
#             'simulate_thoughts', thought_simulator, input_data)
#         evaluate_task = self.task_factory.create_task(
#             'evaluate_thoughts', thought_evaluator)
        
#         # Set up crew
#         return Crew(
#             agents=[thought_simulator, thought_evaluator],
#             tasks=[simulate_task, evaluate_task],
#             process=Process.sequential,
#             verbose=2
#         )
    
#     def create_council_crew(self, thought_process):
#         # Create agents
#         governance = self.agent_factory.create_agent('governance_agent')
#         strategy = self.agent_factory.create_agent('strategy_agent')
#         quality = self.agent_factory.create_agent('quality_agent')
        
#         # Create tasks
#         gov_task = self.task_factory.create_task(
#             'governance_review', governance, thought_process)
#         strat_task = self.task_factory.create_task(
#             'strategy_review', strategy, thought_process)
#         qual_task = self.task_factory.create_task(
#             'quality_review', quality, thought_process)
        
#         # Set up crew
#         return Crew(
#             agents=[governance, strategy, quality],
#             tasks=[gov_task, strat_task, qual_task],
#             process=Process.sequential,
#             verbose=2
#         )
    
#     def create_correction_crew(self, original_output, issues):
#         # Create agents
#         detector = self.agent_factory.create_agent('drift_detector')
#         adjuster = self.agent_factory.create_agent('prompt_adjuster')
#         feedback = self.agent_factory.create_agent('feedback_injector')
        
#         # Create tasks
#         detect_task = self.task_factory.create_task(
#             'detect_drift', detector, f"{original_output}\n\nIssues:{issues}")
#         adjust_task = self.task_factory.create_task(
#             'adjust_prompts', adjuster)
#         feedback_task = self.task_factory.create_task(
#             'inject_feedback', feedback)
        
#         # Set up crew
#         return Crew(
#             agents=[detector, adjuster, feedback],
#             tasks=[detect_task, adjust_task, feedback_task],
#             process=Process.sequential,
#             verbose=2
#         )


# from crewai import Agent, Crew, Process, Task
# from crewai.project import CrewBase, agent, crew, task
# from crewai.agents.agent_builder.base_agent import BaseAgent
# from typing import List

# @CrewBase
# class CrewaiAgents():
#     """CrewaiAgents crew"""

#     agents: List[BaseAgent]
#     tasks: List[Task]

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

#         return Crew(
#             agents=self.agents, # Automatically created by the @agent decorator
#             tasks=self.tasks, # Automatically created by the @task decorator
#             process=Process.sequential,
#             verbose=True,
#             # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
#         )
