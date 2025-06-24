# main.py
from fastapi import FastAPI, HTTPException
from database import Session, ConversationLog
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class LogItem(BaseModel):
    workspace_id: str
    prompt: str
    response: str
    sent_by: str

@app.post("/log_conversation/")
async def log_conversation(item: LogItem):
    session = Session()
    try:
        log = ConversationLog(
            workspace_id=item.workspace_id,
            prompt=item.prompt,
            original_response=item.response,
            sent_by=item.sent_by
        )
        session.add(log)
        session.commit()
        return {"message": "Conversation logged successfully", "id": log.id}
    finally:
        session.close()

@app.get("/get_corrected_response/{log_id}")
async def get_corrected_response(log_id: int):
    session = Session()
    try:
        log = session.query(ConversationLog).filter_by(id=log_id).first()
        if not log:
            raise HTTPException(status_code=404, detail="Log not found")
        return {
            "original_response": log.original_response,
            "corrected_response": log.corrected_response,
            "is_flagged": bool(log.is_flagged)
        }
    finally:
        session.close()