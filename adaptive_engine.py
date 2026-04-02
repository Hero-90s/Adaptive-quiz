# Core/Engine/adaptive_engine.py
import time
import random
import logging
from typing import Optional, List, Dict
from dataclasses import dataclass

from Core.AI.llm_groq import LLMGroq, Question

logger = logging.getLogger(__name__)


class AdaptiveEngine:
    """
    Advanced Adaptive Learning Engine
    Features:
    - Strict 10 question limit
    - No repeated questions
    - Smart difficulty adaptation based on performance
    - Weak topic detection
    - Global ranking/scoreboard
    """

    def __init__(self):
        self.llm = LLMGroq(temperature=0.65)
        self.current_session: Dict[str, Dict] = {}           # student_id -> session data
        self.student_progress: Dict[str, Dict] = {}          # student_id -> progress
        self.teacher_questions: List[Question] = []          # Teacher added questions
        self.global_leaderboard: List[Dict] = []             # Ranking system
        self.asked_questions: Dict[str, set] = {}            # student_id -> set of question IDs (anti-repeat)

        logger.info("Advanced AdaptiveEngine initialized with anti-repeat + ranking")

    def start_session(self, student_id: str, topic: str):
        """Start a fresh session"""
        self.current_session[student_id] = {
            "topic": topic,
            "current_difficulty": 2.5,
            "questions_asked": 0,
            "correct_answers": 0,
            "weak_topics": [],
            "score": 0
        }

        self.student_progress[student_id] = {
            "topic_mastery": {},
            "total_questions": 0,
            "accuracy": 0.0,
            "best_score": 0
        }

        self.asked_questions[student_id] = set()   # Track asked question IDs

        logger.info(f"New session started for {student_id} | Topic: {topic}")

    def get_question(self, student_id: str) -> Question:
        """Get next question - Max 10 questions, no repeats"""
        if student_id not in self.current_session:
            self.start_session(student_id, "Cyber Security")

        session_data = self.current_session[student_id]

        # === STRICT 10 QUESTION LIMIT ===
        if session_data["questions_asked"] >= 10:
            raise Exception("Quiz completed - 10 questions limit reached")

        topic = session_data["topic"]
        target_difficulty = session_data["current_difficulty"]

        # 1. Try teacher questions first (with anti-repeat)
        available_teacher = [q for q in self.teacher_questions 
                           if q.id not in self.asked_questions[student_id] 
                           and q.topic.lower() == topic.lower()]

        if available_teacher:
            q = random.choice(available_teacher)
            self.asked_questions[student_id].add(q.id)
            session_data["questions_asked"] += 1
            return q

        # 2. Generate fresh adaptive question using LLM
        try:
            q = self.llm.generate_adaptive_question(
                topic=topic,
                target_difficulty=target_difficulty,
                student_weak_topics=session_data.get("weak_topics", []),
                student_id=student_id
            )

            # Prevent repeats
            while q.id in self.asked_questions[student_id]:
                q = self.llm.generate_adaptive_question(
                    topic=topic,
                    target_difficulty=target_difficulty,
                    student_weak_topics=session_data.get("weak_topics", []),
                    student_id=student_id
                )

            self.asked_questions[student_id].add(q.id)
            session_data["questions_asked"] += 1
            return q

        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            session_data["questions_asked"] += 1

            # Safe fallback (unique ID)
            fallback_id = f"fallback_{int(time.time())}_{random.randint(1000,9999)}"
            return Question(
                id=fallback_id,
                question=f"Explain a key concept in {topic} at medium difficulty.",
                answer="A",
                topic=topic,
                difficulty=2.5,
                options=[
                    "A. Core foundational concept",
                    "B. Common misconception",
                    "C. Advanced variation",
                    "D. Related but different concept"
                ],
                explanation="This is a safe fallback question.",
                source="fallback"
            )

    def submit_answer(self, student_id: str, question: Question, user_answer: str,
                      response_time: int = 15, confidence: float = 0.7) -> Dict:
        """Process answer with smart adaptation"""
        if student_id not in self.current_session:
            self.start_session(student_id, question.topic)

        session_data = self.current_session[student_id]
        is_correct = user_answer.strip().upper() == question.answer.strip().upper()

        # Update counters
        session_data["correct_answers"] = session_data.get("correct_answers", 0) + (1 if is_correct else 0)
        asked = session_data["questions_asked"]

        # === SMART ADAPTATION BASED ON USER PERFORMANCE ===
        if is_correct:
            # Reward correct answers
            session_data["current_difficulty"] = min(5.0, session_data["current_difficulty"] + 0.35)
            session_data["score"] = session_data.get("score", 0) + int(10 * session_data["current_difficulty"])
            message = "✅ Excellent! Difficulty increased."
        else:
            # Penalize wrong answers + learn weak topics
            session_data["current_difficulty"] = max(1.0, session_data["current_difficulty"] - 0.45)
            session_data["score"] = session_data.get("score", 0) + 2   # Small points for attempt

            # Track weak topics for better future adaptation
            if question.concept_focus and question.concept_focus not in session_data["weak_topics"]:
                session_data["weak_topics"].append(question.concept_focus)

            message = f"❌ Correct answer was **{question.answer}**. {question.explanation or ''}"

        # Calculate accuracy
        accuracy = (session_data["correct_answers"] / asked) * 100 if asked > 0 else 0

        # Update global progress
        self.student_progress[student_id]["accuracy"] = round(accuracy, 1)
        self.student_progress[student_id]["total_questions"] = asked

        result = {
            "correct": is_correct,
            "message": message,
            "new_difficulty": round(session_data["current_difficulty"], 1),
            "accuracy": round(accuracy, 1),
            "questions_asked": asked,
            "correct_count": session_data["correct_answers"],
            "current_score": session_data.get("score", 0),
            "weak_topics": session_data.get("weak_topics", []),
            "explanation": question.explanation or ""
        }

        logger.info(f"{student_id} answered Q{asked}: {'Correct' if is_correct else 'Wrong'} | "
                   f"Difficulty: {result['new_difficulty']} | Score: {result['current_score']}")

        return result

    def add_teacher_question(self, question_text: str, correct_answer: str,
                             topic: str = "Cyber Security", options: Optional[List[str]] = None):
        """Add question from teacher"""
        if not options or len(options) != 4:
            options = [f"A. {correct_answer}", "B. Option B", "C. Option C", "D. Option D"]

        q = Question(
            id=f"teacher_{int(time.time())}_{random.randint(100,999)}",
            question=question_text,
            answer=correct_answer.upper(),
            topic=topic,
            difficulty=3.0,
            options=options,
            explanation="Added by teacher.",
            source="teacher"
        )
        self.teacher_questions.append(q)
        logger.info(f"Teacher MCQ added for {topic}")
        return q

    def get_student_stats(self, student_id: str) -> Dict:
        """Get detailed stats"""
        session = self.current_session.get(student_id, {})
        progress = self.student_progress.get(student_id, {})
        return {
            "score": session.get("score", 0),
            "accuracy": progress.get("accuracy", 0),
            "questions_asked": session.get("questions_asked", 0),
            "weak_topics": session.get("weak_topics", []),
            "current_difficulty": session.get("current_difficulty", 2.5)
        }

    # ====================== RANKING SYSTEM ======================
    def update_leaderboard(self, student_id: str, final_score: int, accuracy: float, topic: str):
        """Update global ranking"""
        entry = {
            "student_id": student_id,
            "score": final_score,
            "accuracy": round(accuracy, 1),
            "topic": topic,
            "timestamp": time.time()
        }

        # Remove old entry if exists
        self.global_leaderboard = [e for e in self.global_leaderboard if e["student_id"] != student_id]
        self.global_leaderboard.append(entry)

        # Sort by score descending
        self.global_leaderboard.sort(key=lambda x: x["score"], reverse=True)

        # Keep top 20 only
        self.global_leaderboard = self.global_leaderboard[:20]

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Return current ranking"""
        return self.global_leaderboard[:limit]