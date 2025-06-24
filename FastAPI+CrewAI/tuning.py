# correction.py
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class SemanticDriftCorrector:
    def __init__(self):
        self.llm = OpenAI(temperature=0.3)
        self.correction_template = PromptTemplate(
            input_variables=["original_prompt", "original_response", "correction_notes"],
            template="""
            The following AI response was flagged by the ethical review system:
            
            Original Prompt: {original_prompt}
            Original Response: {original_response}
            
            Correction Notes: {correction_notes}
            
            Please rewrite the response to address these concerns while maintaining helpfulness.
            The corrected response should be truthful, ethical, and harmless.
            """
        )
    
    def correct_response(self, original_prompt: str, original_response: str, correction_notes: str) -> str:
        chain = LLMChain(llm=self.llm, prompt=self.correction_template)
        corrected = chain.run({
            "original_prompt": original_prompt,
            "original_response": original_response,
            "correction_notes": correction_notes
        })
        return corrected.strip()