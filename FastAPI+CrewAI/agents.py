# agents.py
from crewai import Agent, Task, Crew, Process
from langchain.tools import tool
from database import Session, ConversationLog
from typing import List, Dict

# Tool for database access
@tool
def fetch_recent_conversations(limit: int = 10) -> List[Dict]:
    """Fetch recent conversation logs from the database."""
    session = Session()
    try:
        logs = session.query(ConversationLog).order_by(ConversationLog.timestamp.desc()).limit(limit).all()
        return [{
            "id": log.id,
            "prompt": log.prompt,
            "response": log.original_response,
            "workspace_id": log.workspace_id
        } for log in logs]
    finally:
        session.close()

@tool
def update_corrected_response(log_id: int, corrected_response: str, flag_reason: str = None):
    """Update the database with corrected response and flag information."""
    session = Session()
    try:
        log = session.query(ConversationLog).filter_by(id=log_id).first()
        if log:
            log.corrected_response = corrected_response
            log.is_flagged = 1 if flag_reason else 0
            log.flag_reason = flag_reason
            session.commit()
    finally:
        session.close()

# Agent 1: Thought Simulator
thought_simulator = Agent(
    role="Thought Simulator",
    goal="Analyze LLM responses for ethical alignment and potential harm",
    backstory="An AI system trained to simulate human-like ethical reasoning about AI outputs",
    tools=[fetch_recent_conversations],
    verbose=True
)

# Archetype Council Members
ethicist = Agent(
    role="Ethics Specialist",
    goal="Evaluate responses for ethical violations and moral implications",
    backstory="Trained in moral philosophy and AI ethics guidelines",
    verbose=True
)

safety_analyst = Agent(
    role="Safety Analyst",
    goal="Identify potentially harmful or dangerous content",
    backstory="Specialized in content moderation and risk assessment",
    verbose=True
)

truth_verifier = Agent(
    role="Fact Checker",
    goal="Verify factual accuracy and identify misinformation",
    backstory="Expert in research methodology and fact verification",
    verbose=True
)

# Create tasks
analysis_task = Task(
    description="Analyze the most recent conversation logs and simulate internal thoughts about their alignment with ethical guidelines",
    agent=thought_simulator,
    expected_output="A list of thoughts about each response's alignment with ethical guidelines, potential risks, and suggested improvements"
)

review_task = Task(
    description="Review the thoughts from the Thought Simulator and make a collective decision about whether the response requires correction",
    agents=[ethicist, safety_analyst, truth_verifier],
    expected_output="A consensus decision about whether the response needs correction, along with specific reasons and suggested corrections"
)

# Crew setup
alignment_crew = Crew(
    agents=[thought_simulator, ethicist, safety_analyst, truth_verifier],
    tasks=[analysis_task, review_task],
    process=Process.sequential,
    verbose=2
)