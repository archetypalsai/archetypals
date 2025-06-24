# models.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ConversationLog(Base):
    __tablename__ = 'conversation_logs'
    
    id = Column(Integer, primary_key=True)
    workspace_id = Column(String(50), nullable=False)
    prompt = Column(Text, nullable=False)
    original_response = Column(Text)
    corrected_response = Column(Text)
    sent_by = Column(String(50))
    timestamp = Column(DateTime, server_default='CURRENT_TIMESTAMP')
    is_flagged = Column(Integer, default=0)
    flag_reason = Column(Text)
    
# Initialize database
engine = create_engine('sqlite:///conversation_logs.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)