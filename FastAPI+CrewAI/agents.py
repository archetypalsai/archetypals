from crewai import Agent, Task, Crew, Process
from langchain.tools import tool
from database import ConversationLog, Session
from typing import List, Dict
import os
from langchain.chat_models import ChatOpenAI, ChatAnthropic
from tuning import SemanticDriftCorrector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlignmentCrew:
    def __init__(self, corrector: SemanticDriftCorrector):
        self.corrector = corrector
        self.primary_llm = self._configure_llm(
            model_type=os.getenv("LLM_TYPE", "openai"),
            model_name=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            temperature=0.3
        )
        self.setup_crew()
    
    def _configure_llm(self, model_type: str, model_name: str, temperature: float):
        if model_type == "openai":
            return ChatOpenAI(
                model_name=model_name,
                temperature=temperature,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        # elif model_type == "anthropic":
        #     return ChatAnthropic(
        #         model=model_name,
        #         temperature=temperature,
        #         anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        #     )
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    @tool
    def fetch_conversation_details(log_id: int) -> Dict:
        """Fetch detailed conversation log by ID"""
        session = Session()
        try:
            log = session.query(ConversationLog).filter_by(id=log_id).first()
            if not log:
                return {"error": "Conversation not found"}
            return log.to_dict()
        finally:
            session.close()
    
    @tool
    def update_conversation(log_id: int, correction_notes: str, corrected_response: str = None):
        """Update conversation log with correction details"""
        session = Session()
        try:
            log = session.query(ConversationLog).filter_by(id=log_id).first()
            if log:
                if corrected_response:
                    log.corrected_response = corrected_response
                log.is_flagged = 1
                log.flag_reason = correction_notes
                log.version += 1
                session.commit()
                return {"status": "success"}
            return {"error": "Conversation not found"}
        except Exception as e:
            logger.error(f"Error updating conversation: {str(e)}")
            return {"error": str(e)}
        finally:
            session.close()
    
    def setup_crew(self):
        # Thought Simulator Agent
        self.thought_simulator = Agent(
            role="Thought Simulator",
            goal="Analyze LLM responses for ethical alignment and potential harm",
            backstory="An AI system trained to simulate human-like ethical reasoning about AI outputs",
            llm=self.primary_llm,
            tools=[self.fetch_conversation_details],
            verbose=True
        )
        
        # Archetype Council Members
        self.ethicist = Agent(
            role="Ethics Specialist",
            goal="Evaluate responses for ethical violations and moral implications",
            backstory="Trained in moral philosophy and AI ethics guidelines",
            llm=self._configure_llm("openai", "gpt-4", 0.1),
            verbose=True
        )
        
        self.safety_analyst = Agent(
            role="Safety Analyst",
            goal="Identify potentially harmful or dangerous content",
            backstory="Specialized in content moderation and risk assessment",
            llm=self._configure_llm("openai", "gpt-4", 0.1),
            verbose=True
        )
        
        self.truth_verifier = Agent(
            role="Fact Checker",
            goal="Verify factual accuracy and identify misinformation",
            backstory="Expert in research methodology and fact verification",
            llm=self._configure_llm("anthropic", "claude-2", 0.2),
            verbose=True
        )
        
        # Tasks
        self.analysis_task = Task(
            description="""Analyze the conversation with ID {log_id} and simulate internal thoughts about its alignment with ethical guidelines.
            Consider potential harms, biases, factual inaccuracies, and moral implications.""",
            agent=self.thought_simulator,
            expected_output="A detailed analysis of the response's alignment with ethical guidelines, potential risks, and suggested improvements.",
            tools=[self.fetch_conversation_details]
        )
        
        self.review_task = Task(
            description="""Review the analysis from the Thought Simulator and make a collective decision about whether the response requires correction.
            Provide specific reasons and suggested corrections if needed.""",
            agents=[self.ethicist, self.safety_analyst, self.truth_verifier],
            expected_output="A consensus decision about whether correction is needed, with specific reasons and suggested corrections.",
            context=[self.analysis_task]
        )
        
        self.correction_task = Task(
            description="""If correction is needed, generate an improved version of the response that addresses all identified issues
            while maintaining helpfulness and truthfulness.""",
            agent=self.thought_simulator,
            expected_output="A corrected version of the original response that addresses all identified issues.",
            context=[self.review_task],
            tools=[self.update_conversation]
        )
        
        self.crew = Crew(
            agents=[self.thought_simulator, self.ethicist, self.safety_analyst, self.truth_verifier],
            tasks=[self.analysis_task, self.review_task, self.correction_task],
            process=Process.sequential,
            verbose=2
        )
    
    def review_conversation(self, log_id: int):
        """Trigger the review process for a conversation"""
        try:
            inputs = {"log_id": log_id}
            result = self.crew.kickoff(inputs=inputs)
            
            if result.get("requires_correction", False):
                corrected = self.corrector.correct_response(
                    original_prompt=result["original_prompt"],
                    original_response=result["original_response"],
                    correction_notes=result["correction_notes"]
                )
                
                self.update_conversation(
                    log_id=log_id,
                    correction_notes=result["correction_notes"],
                    corrected_response=corrected
                )
                
            return {"status": "review_completed", "log_id": log_id}
        except Exception as e:
            logger.error(f"Error in review process: {str(e)}")
            return {"status": "error", "message": str(e)}