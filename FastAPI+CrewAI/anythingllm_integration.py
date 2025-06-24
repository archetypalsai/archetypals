# anythingllm_integration.py
import requests
from fastapi import APIRouter
from models import Session, ConversationLog
from agents import alignment_crew
from tuning import SemanticDriftCorrector

router = APIRouter()
corrector = SemanticDriftCorrector()

@router.post("/review_and_correct")
async def review_and_correct():
    # Step 1: Get recent conversations
    session = Session()
    try:
        # Get the most recent unflagged conversation
        conversation = session.query(ConversationLog).filter_by(is_flagged=0).order_by(ConversationLog.timestamp.desc()).first()
        
        if not conversation:
            return {"status": "no new conversations to review"}
        
        # Step 2: Run through alignment crew
        inputs = {"conversation_id": conversation.id}
        results = alignment_crew.kickoff(inputs=inputs)
        
        # Step 3: If flagged, perform correction
        if "requires_correction" in results and results["requires_correction"]:
            corrected_response = corrector.correct_response(
                original_prompt=conversation.prompt,
                original_response=conversation.original_response,
                correction_notes=results["correction_notes"]
            )
            
            # Update database
            conversation.corrected_response = corrected_response
            conversation.is_flagged = 1
            conversation.flag_reason = results["correction_notes"]
            session.commit()
            
            return {
                "status": "correction_applied",
                "original_response": conversation.original_response,
                "corrected_response": corrected_response
            }
        
        return {"status": "no_correction_needed"}
    
    finally:
        session.close()