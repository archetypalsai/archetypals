from typing import List, Dict, Optional
from pydantic import BaseModel
import yaml
from pathlib import Path
import requests
from config.settings import settings

class SafetyTool(BaseModel):
    name: str
    description: str
    
    class Config:
        arbitrary_types_allowed = True

class HarmDetectionTool(SafetyTool):
    name: str = "harm_detection"
    description: str = "Detects harmful, violent, or dangerous content"
    
    def __init__(self):
        super().__init__()
        self.blocklist = self._load_blocklist()
    
    def _load_blocklist(self) -> List[str]:
        with open(Path(__file__).parent.parent / "config" / "constitution.yaml") as f:
            data = yaml.safe_load(f)
            return data.get("harm_blocklist", [])
    
    def run(self, text: str) -> Dict:
        violations = []
        for term in self.blocklist:
            if term.lower() in text.lower():
                violations.append(term)
        
        return {
            "is_safe": len(violations) == 0,
            "violations": violations,
            "score": len(violations) / max(1, len(text.split()))
        }

class EthicsCheckTool(SafetyTool):
    name: str = "ethics_check"
    description: str = "Validates compliance with ethical guidelines"
    
    def __init__(self):
        super().__init__()
        self.ethics_rules = self._load_ethics_rules()
    
    def _load_ethics_rules(self) -> Dict:
        with open(Path(__file__).parent.parent / "config" / "constitution.yaml") as f:
            data = yaml.safe_load(f)
            return data.get("ethics_rules", {})
    
    def run(self, text: str) -> Dict:
        violations = []
        
        # Check for fairness and bias
        if any(bias_term in text.lower() for bias_term in self.ethics_rules.get("bias_terms", [])):
            violations.append("potential_bias")
        
        # Check for privacy violations
        if any(priv_term in text.lower() for priv_term in self.ethics_rules.get("privacy_terms", [])):
            violations.append("privacy_risk")
            
        return {
            "is_compliant": len(violations) == 0,
            "violations": violations
        }

class FactCheckTool(SafetyTool):
    name: str = "fact_check"
    description: str = "Verifies factual claims against trusted sources"
    
    def run(self, text: str) -> Dict:
        # In a production system, this would integrate with fact-checking APIs
        # For now, we'll simulate with a simple implementation
        questionable_claims = []
        
        # This would be replaced with actual API calls in production
        if "scientific consensus" in text.lower() and "study shows" not in text.lower():
            questionable_claims.append("Missing citation for scientific claim")
            
        return {
            "is_accurate": len(questionable_claims) == 0,
            "inaccuracies": questionable_claims,
            "sources": []  # Would contain verified sources in production
        }

# Tool registry
SAFETY_TOOLS = {
    "harm_detection": HarmDetectionTool(),
    "ethics_check": EthicsCheckTool(),
    "fact_check": FactCheckTool()
}