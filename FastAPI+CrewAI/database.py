from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class ConversationLog(Base):
    __tablename__ = 'conversation_logs'
    
    id = Column(Integer, primary_key=True)
    workspace_id = Column(String(50), nullable=False)
    prompt = Column(Text, nullable=False)
    original_response = Column(Text)
    corrected_response = Column(Text)
    sent_by = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_flagged = Column(Integer, default=0)
    flag_reason = Column(Text)
    review_notes = Column(Text)
    version = Column(Integer, default=1)
    
    def to_dict(self):
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "prompt": self.prompt,
            "original_response": self.original_response,
            "corrected_response": self.corrected_response,
            "is_flagged": bool(self.is_flagged),
            "flag_reason": self.flag_reason,
            "version": self.version
        }

# Initialize database
engine = create_engine('sqlite:///conversation_logs.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)