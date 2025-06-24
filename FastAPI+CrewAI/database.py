################ 1. Database Setup (SQLite) #################

# database.py
import sqlite3
from typing import List, Dict, Any
from datetime import datetime

class ThoughtDatabase:
    def __init__(self, db_path: str = "thoughts.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS thoughts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            thought_text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metadata JSON
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thought_id INTEGER,
            archetype_id TEXT,
            decision TEXT,
            confidence FLOAT,
            reasoning TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (thought_id) REFERENCES thoughts(id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tuning_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            tuning_type TEXT,
            parameters JSON,
            before_state TEXT,
            after_state TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()

    def log_thought(self, agent_id: str, thought_text: str, metadata: dict = None):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO thoughts (agent_id, thought_text, metadata) VALUES (?, ?, ?)",
            (agent_id, thought_text, str(metadata) if metadata else None)
        )
        self.conn.commit()
        return cursor.lastrowid

    def log_decision(self, thought_id: int, archetype_id: str, decision: str, confidence: float, reasoning: str):
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO decisions 
            (thought_id, archetype_id, decision, confidence, reasoning) 
            VALUES (?, ?, ?, ?, ?)""",
            (thought_id, archetype_id, decision, confidence, reasoning)
        )
        self.conn.commit()

    def get_recent_thoughts(self, limit: int = 10) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT t.*, d.decision, d.confidence, d.archetype_id 
        FROM thoughts t
        LEFT JOIN decisions d ON t.id = d.thought_id
        ORDER BY t.timestamp DESC
        LIMIT ?
        """, (limit,))
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def close(self):
        self.conn.close()