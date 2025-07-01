from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime
import uuid

class AlignmentLevel(str, Enum):
    FULL = "fully_aligned"
    PARTIAL = "partially_aligned"
    MISALIGNED = "misaligned"

class DriftSeverity(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlignmentReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str
    thought_process: str
    logical_consistency_score: float = Field(..., ge=0, le=1)
    bias_detected: List[str] = Field(default_factory=list)
    alignment_level: AlignmentLevel
    improvement_suggestions: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)

class CouncilVote(BaseModel):
    agent_role: str
    decision: str
    confidence: float = Field(..., ge=0, le=1)
    comments: str
    suggested_changes: Optional[List[str]] = None

class CouncilDecision(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    report_id: str
    votes: List[CouncilVote]
    final_decision: str
    drift_detected: bool = False
    drift_severity: DriftSeverity = DriftSeverity.NONE
    correction_required: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)

class PromptCorrection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    original_prompt: str
    corrected_prompt: str
    correction_reason: str
    expected_impact: str
    timestamp: datetime = Field(default_factory=datetime.now)