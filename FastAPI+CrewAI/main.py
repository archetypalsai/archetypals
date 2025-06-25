from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import Session, ConversationLog
from pydantic import BaseModel
from datetime import datetime
from typing import List
import logging
from tuning import SemanticDriftCorrector
from agents import AlignmentCrew
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LogItem(BaseModel):
    workspace_id: str
    prompt: str
    response: str
    sent_by: str

class CorrectionRequest(BaseModel):
    log_id: int
    correction_notes: str

# Initialize components
corrector = SemanticDriftCorrector(
    model_type=os.getenv("LLM_TYPE", "openai"),
    model_name=os.getenv("LLM_MODEL", "gpt-4")
)

alignment_crew = AlignmentCrew(corrector=corrector)

# Dependency for database session
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

@app.post("/log_conversation/")
async def log_conversation(item: LogItem, db: Session = Depends(get_db)): # type: ignore
    """Endpoint to log new conversations from AnythingLLM"""
    try:
        log = ConversationLog(
            workspace_id=item.workspace_id,
            prompt=item.prompt,
            original_response=item.response,
            sent_by=item.sent_by
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        
        # Trigger async review
        alignment_crew.review_conversation(log.id)
        
        return {"message": "Conversation logged successfully", "log_id": log.id}
    except Exception as e:
        logger.error(f"Error logging conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/get_conversation/{log_id}")
async def get_conversation(log_id: int, db: Session = Depends(get_db)):
    """Retrieve a conversation by ID"""
    log = db.query(ConversationLog).filter_by(id=log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return log.to_dict()

@app.post("/request_correction/")
async def request_correction(request: CorrectionRequest, db: Session = Depends(get_db)):
    """Manually request correction for a conversation"""
    log = db.query(ConversationLog).filter_by(id=request.log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    corrected = corrector.correct_response(
        original_prompt=log.prompt,
        original_response=log.original_response,
        correction_notes=request.correction_notes
    )
    
    log.corrected_response = corrected
    log.is_flagged = 1
    log.flag_reason = request.correction_notes
    log.version += 1
    db.commit()
    
    return {
        "status": "correction_applied",
        "original_response": log.original_response,
        "corrected_response": corrected
    }

@app.get("/review_queue/")
async def get_review_queue(limit: int = 10, db: Session = Depends(get_db)):
    """Get conversations needing review"""
    logs = db.query(ConversationLog).filter_by(is_flagged=0).order_by(ConversationLog.timestamp.desc()).limit(limit).all()
    return [log.to_dict() for log in logs]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)