# core/memory/long_term_memory.py

import json
import time
import sqlite3
import logging
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class StudentKnowledge:
    """Long-term knowledge profile for a student."""
    student_id: str
    elo_rating: float = 1000.0
    total_sessions: int = 0
    total_correct: int = 0
    topic_mastery: Dict[str, float] = field(default_factory=dict)
    last_practiced: Dict[str, float] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    last_updated: float = field(default_factory=time.time)

    def __post_init__(self):
        if not self.topic_mastery:
            self.topic_mastery = {}
        if not self.last_practiced:
            self.last_practiced = {}


class LongTermMemory:
    def __init__(self, db_path: str = "database/student_longterm.db"):
        self.db_path = db_path
        self._init_database()
        self.in_memory_cache: Dict[str, StudentKnowledge] = {}

    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_profiles (
                student_id TEXT PRIMARY KEY,
                elo_rating REAL DEFAULT 1000.0,
                total_sessions INTEGER DEFAULT 0,
                total_correct INTEGER DEFAULT 0,
                last_updated TEXT,
                data JSON
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topic_mastery (
                student_id TEXT,
                topic TEXT,
                mastery REAL DEFAULT 0.5,
                last_practiced TEXT,
                PRIMARY KEY (student_id, topic)
            )
        """)
        conn.commit()
        conn.close()

    def get_student_knowledge(self, student_id: str) -> StudentKnowledge:
        if student_id in self.in_memory_cache:
            return self.in_memory_cache[student_id]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM student_profiles WHERE student_id = ?", (student_id,))
        row = cursor.fetchone()

        if row:
            data = json.loads(row[5]) if row[5] else {}
            knowledge = StudentKnowledge(
                student_id=student_id,
                elo_rating=row[1],
                total_sessions=row[2],
                total_correct=row[3],
                topic_mastery=data.get("topic_mastery", {}),
                last_practiced=data.get("last_practiced", {}),
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", [])
            )
        else:
            knowledge = StudentKnowledge(student_id=student_id)

        # Load topic mastery
        cursor.execute("SELECT topic, mastery, last_practiced FROM topic_mastery WHERE student_id = ?", (student_id,))
        for topic, mastery, last_practiced in cursor.fetchall():
            knowledge.topic_mastery[topic] = mastery
            if last_practiced:
                knowledge.last_practiced[topic] = datetime.fromisoformat(last_practiced).timestamp()

        conn.close()
        self.in_memory_cache[student_id] = knowledge
        return knowledge

    def update_after_session(self, student_id: str, topic: str, is_correct: bool, difficulty: float, response_time: float = 0.0):
        knowledge = self.get_student_knowledge(student_id)
        current_time = time.time()

        if topic not in knowledge.topic_mastery:
            knowledge.topic_mastery[topic] = 0.4

        learning_rate = 0.22 if is_correct else -0.11
        if difficulty > 3.5 and is_correct:
            learning_rate += 0.08

        knowledge.topic_mastery[topic] = max(0.1, min(0.98, knowledge.topic_mastery[topic] + learning_rate))
        knowledge.last_practiced[topic] = current_time

        knowledge.total_sessions += 1
        if is_correct:
            knowledge.total_correct += 1

        knowledge.elo_rating = max(600, min(1800, knowledge.elo_rating + (8 if is_correct else -5)))
        knowledge.last_updated = current_time

        self._save_to_database(knowledge)

    def _save_to_database(self, knowledge: StudentKnowledge):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        data = {
            "topic_mastery": dict(knowledge.topic_mastery),
            "last_practiced": knowledge.last_practiced,
            "strengths": knowledge.strengths,
            "weaknesses": knowledge.weaknesses
        }

        cursor.execute("""
            INSERT OR REPLACE INTO student_profiles 
            (student_id, elo_rating, total_sessions, total_correct, last_updated, data)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            knowledge.student_id, knowledge.elo_rating, knowledge.total_sessions,
            knowledge.total_correct, datetime.now().isoformat(), json.dumps(data)
        ))

        for topic, mastery in knowledge.topic_mastery.items():
            last_practiced = datetime.fromtimestamp(knowledge.last_practiced.get(topic, time.time())).isoformat()
            cursor.execute("""
                INSERT OR REPLACE INTO topic_mastery 
                (student_id, topic, mastery, last_practiced)
                VALUES (?, ?, ?, ?)
            """, (knowledge.student_id, topic, mastery, last_practiced))

        conn.commit()
        conn.close()

    def get_weak_topics(self, student_id: str, threshold: float = 0.55, limit: int = 6) -> List[str]:
        knowledge = self.get_student_knowledge(student_id)
        current_time = time.time()
        weak = []

        for topic, mastery in knowledge.topic_mastery.items():
            days_since = (current_time - knowledge.last_practiced.get(topic, 0)) / 86400
            decayed = mastery * (0.94 ** max(0, days_since - 2))
            if decayed < threshold:
                weak.append((topic, decayed))

        weak.sort(key=lambda x: x[1])
        return [t[0] for t in weak[:limit]]

    def get_overall_progress(self, student_id: str) -> Dict:
        knowledge = self.get_student_knowledge(student_id)
        if not knowledge.topic_mastery:
            return {"overall_mastery": 0.0, "message": "Start practicing!"}

        avg_mastery = sum(knowledge.topic_mastery.values()) / len(knowledge.topic_mastery)
        return {
            "overall_mastery": round(avg_mastery * 100, 1),
            "total_topics": len(knowledge.topic_mastery),
            "elo_rating": round(knowledge.elo_rating),
            "total_sessions": knowledge.total_sessions,
            "last_active": datetime.fromtimestamp(knowledge.last_updated).strftime("%d %b %Y")
        }