from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime
from enum import Enum
import uuid

class AlignmentClassification(str, Enum):
    FULL = "full_alignment"
    PARTIAL = "partial_alignment"
    MISALIGNED = "misaligned"
    UNKNOWN = "unknown"

class DriftSeverity(str, Enum):
    NONE = "none"
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"

class CorrectionMethod(str, Enum):
    PROMPT_ADJUSTMENT = "prompt_adjustment"
    FEEDBACK_INJECTION = "feedback_injection"
    CONTEXT_ENHANCEMENT = "context_enhancement"
    MULTI_AGENT_REVIEW = "multi_agent_review"

class ThoughtLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    input_data: str = Field(..., description="Original input that triggered the thought process")
    simulated_thoughts: str = Field(..., description="Generated thought process output")
    evaluation_notes: Optional[str] = Field(None, description="Initial evaluation notes from thought evaluator")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata about the thought process")

    class Config:
        json_schema_extra = {
            "example": {
                "input_data": "How should we approach our new product launch?",
                "simulated_thoughts": "First consider market research...",
                "evaluation_notes": "Logical flow but lacks competitor analysis",
                "metadata": {"source": "marketing_team"}
            }
        }

class CouncilVote(BaseModel):
    agent_role: str = Field(..., description="Role of the voting agent")
    vote: Literal["approve", "reject", "modify"] = Field(..., description="Vote decision")
    comments: str = Field(..., description="Detailed comments from the agent")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level in the vote")

class CouncilDecision(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    thought_log_id: str = Field(..., description="Reference to the thought log being evaluated")
    votes: List[CouncilVote] = Field(..., description="Individual votes from council members")
    final_decision: str = Field(..., description="Synthesized final decision")
    alignment_classification: AlignmentClassification = Field(...)
    drift_detected: bool = Field(False)
    drift_severity: DriftSeverity = Field(DriftSeverity.NONE)
    timestamp: datetime = Field(default_factory=datetime.now)
    discussion_summary: Optional[str] = Field(None, description="Summary of council discussion")

    class Config:
        json_schema_extra = {
            "example": {
                "thought_log_id": "123e4567-e89b-12d3-a456-426614174000",
                "votes": [
                    {
                        "agent_role": "Governance",
                        "vote": "approve",
                        "comments": "Complies with all policies",
                        "confidence": 0.9
                    }
                ],
                "final_decision": "Approved with minor suggestions",
                "alignment_classification": "full_alignment",
                "drift_detected": False
            }
        }

class CorrectionHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str = Field(..., description="Reference to the council decision that triggered correction")
    original_output: str = Field(..., description="Original output before correction")
    corrected_output: str = Field(..., description="Output after applying corrections")
    correction_reason: str = Field(..., description="Rationale for the correction")
    correction_method: List[CorrectionMethod] = Field(..., description="Methods used for correction")
    applied_changes: List[str] = Field(..., description="Specific changes made during correction")
    timestamp: datetime = Field(default_factory=datetime.now)
    effectiveness_score: Optional[float] = Field(None, ge=0, le=1, description="Post-correction effectiveness rating")

    class Config:
        json_schema_extra = {
            "example": {
                "decision_id": "123e4567-e89b-12d3-a456-426614174000",
                "original_output": "Original strategy draft...",
                "corrected_output": "Revised strategy with compliance...",
                "correction_reason": "Missing regulatory considerations",
                "correction_method": ["prompt_adjustment", "context_enhancement"],
                "applied_changes": [
                    "Added regulatory compliance section",
                    "Enhanced risk assessment"
                ]
            }
        }

class WorkflowAudit(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_run_id: str = Field(..., description="Identifier for the complete workflow run")
    start_time: datetime = Field(...)
    end_time: Optional[datetime] = Field(None)
    processing_steps: List[str] = Field(..., description="Sequence of processing steps executed")
    status: Literal["running", "completed", "failed"] = Field(...)
    error_logs: Optional[List[str]] = Field(None)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)