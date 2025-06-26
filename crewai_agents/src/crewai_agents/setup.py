import yaml
from crewai import Agent, Task
from pathlib import Path

class ConfigLoader:
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / "config"
        
    def load_agents(self):
        with open(self.config_path / "agents.yaml", "r") as f:
            return yaml.safe_load(f)
    
    def load_tasks(self):
        with open(self.config_path / "tasks.yaml", "r") as f:
            return yaml.safe_load(f)

class AgentFactory:
    def __init__(self):
        self.loader = ConfigLoader()
        self.agent_configs = self.loader.load_agents()
    
    def create_agent(self, agent_key):
        config = self.agent_configs[agent_key]
        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'],
            verbose=config['verbose'],
            allow_delegation=config['allow_delegation']
        )

class TaskFactory:
    def __init__(self):
        self.loader = ConfigLoader()
        self.task_configs = self.loader.load_tasks()
    
    def create_task(self, task_key, agent, input_data=None):
        config = self.task_configs[task_key]
        description = config['description']
        if input_data:
            description = f"{description}\n\nInput Data:\n{input_data}"
            
        return Task(
            description=description,
            agent=agent,
            expected_output=config['expected_output']
        )