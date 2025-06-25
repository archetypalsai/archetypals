from langchain.chat_models import ChatOpenAI, ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticDriftCorrector:
    def __init__(self, model_type: str = "openai", model_name: str = "gpt-4"):
        """
        Initialize the corrector with specified model
        :param model_type: 'openai' or 'anthropic'
        :param model_name: Model identifier (e.g., 'gpt-4', 'claude-2')
        """
        self.model_type = model_type
        self.model_name = model_name
        
        if model_type == "openai":
            self.llm = ChatOpenAI(
                model_name=model_name,
                temperature=0.3,
                max_tokens=2000,
                openai_api_key=os.getenv("OPENAI_API_KEY")
            )
        elif model_type == "anthropic":
            self.llm = ChatAnthropic(
                model=model_name,
                temperature=0.3,
                max_tokens_to_sample=2000,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        self.correction_template = PromptTemplate(
            input_variables=["original_prompt", "original_response", "correction_notes"],
            template="""
            You are an AI Alignment Specialist tasked with correcting responses that were flagged by the ethical review system.
            
            Original Prompt: {original_prompt}
            
            Original Response (flagged as problematic): 
            {original_response}
            
            Issues Identified:
            {correction_notes}
            
            Please rewrite the response to:
            1. Address all identified issues
            2. Maintain truthfulness and accuracy
            3. Be helpful and cooperative
            4. Avoid any harmful, biased, or unethical content
            5. Preserve the original intent where appropriate
            
            Provide only the corrected response:
            """
        )
    
    def correct_response(self, original_prompt: str, original_response: str, correction_notes: str) -> str:
        try:
            chain = LLMChain(llm=self.llm, prompt=self.correction_template)
            corrected = chain.run({
                "original_prompt": original_prompt,
                "original_response": original_response,
                "correction_notes": correction_notes
            })
            return corrected.strip()
        except Exception as e:
            logger.error(f"Error during correction: {str(e)}")
            # Fallback response
            return "I apologize, but I can't provide that response. Let me try to address your query differently."