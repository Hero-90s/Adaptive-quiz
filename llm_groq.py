# core/ai/llm_groq.py

import os
import time
import logging
import hashlib
import random
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

import dotenv
from groq import Groq, RateLimitError
from pydantic import BaseModel, Field

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# =============================================================
# QUESTION DATACLASS - Enhanced
# =============================================================
@dataclass
class Question:
    """Enhanced Question dataclass used across the system"""
    id: str
    question: str
    answer: str                    # Correct option letter (A/B/C/D) or full answer
    topic: str
    difficulty: float
    # Default fields after required ones
    options: Optional[List[str]] = None
    explanation: Optional[str] = None
    estimated_time: int = 30
    concept_focus: Optional[str] = None
    hint: Optional[str] = None                     # New: helpful hint for students
    source: str = "groq"                           # "groq" or "teacher"


# =============================================================
# PYDANTIC SCHEMA FOR STRUCTURED OUTPUT (MCQ Optimized)
# =============================================================
class QuestionSchema(BaseModel):
    question: str
    answer: str                                    # A/B/C/D or full answer
    options: List[str] = Field(default_factory=list)  # Always 4 options for MCQ
    explanation: str
    difficulty: float = Field(..., ge=1.0, le=5.0)
    estimated_time: int = Field(..., ge=15, le=120)
    concept_focus: str
    hint: Optional[str] = None


# =============================================================
# ADVANCED LLM GROQ CLASS (15+ Features)
# =============================================================
class LLMGroq:
    """
    Production-Grade Groq LLM Handler for Adaptive Learning System.
    15+ Advanced Features Added.
    """

    def __init__(
        self,
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.65,
        max_tokens: int = 1024,
        max_retries: int = 5,
        debug: bool = False
    ):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("❌ GROQ_API_KEY environment variable is not set.")

        self.client = Groq(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.debug = debug

        # Advanced Metrics
        self.total_tokens_used = 0
        self.total_requests = 0
        self.total_latency = 0.0
        self.cost_tracker: Dict[str, float] = {}      # student_id -> total cost

        # Smart Caching with TTL
        self._cache: Dict[str, Tuple[Any, float]] = {}   # key -> (data, timestamp)
        self.cache_ttl = 3600  # 1 hour

        logger.info(f"LLMGroq initialized with model: {model}")

    # =============================================================
    # FEATURE: Smart Caching
    # =============================================================
    def _get_cache_key(self, prompt: str) -> str:
        return hashlib.md5(prompt.encode('utf-8')).hexdigest()

    def _is_cache_valid(self, timestamp: float) -> bool:
        return time.time() - timestamp < self.cache_ttl

    # =============================================================
    # FEATURE: Metrics & Cost Tracking
    # =============================================================
    def _update_metrics(self, response: Any, latency: float, student_id: str = "unknown"):
        try:
            usage = response.usage
            tokens = usage.total_tokens if usage else 0
            self.total_tokens_used += tokens
            self.total_requests += 1
            self.total_latency += latency

            # Approximate Groq cost (adjust as needed)
            cost = tokens * 0.0000008
            self.cost_tracker[student_id] = self.cost_tracker.get(student_id, 0) + cost
        except:
            pass

    def get_usage_stats(self, student_id: Optional[str] = None) -> Dict:
        avg_latency = self.total_latency / self.total_requests if self.total_requests > 0 else 0
        return {
            "total_requests": self.total_requests,
            "total_tokens_used": self.total_tokens_used,
            "avg_latency_seconds": round(avg_latency, 3),
            "estimated_cost_usd": round(self.cost_tracker.get(student_id, 0), 6) if student_id else sum(self.cost_tracker.values())
        }

    # =============================================================
    # MAIN METHOD: Generate Adaptive MCQ Question
    # =============================================================
    def generate_adaptive_question(
        self,
        topic: str,
        target_difficulty: float = 2.5,
        focus_topic: Optional[str] = None,
        trickiness: float = 0.4,
        learning_mode: str = "adaptive_practice",
        student_weak_topics: Optional[List[str]] = None,
        student_id: str = "unknown"
    ) -> Question:
        """Generate high-quality MCQ with all advanced features"""

        prompt = self._build_mcq_prompt(
            topic=topic,
            target_difficulty=target_difficulty,
            focus_topic=focus_topic,
            trickiness=trickiness,
            learning_mode=learning_mode,
            weak_topics=student_weak_topics or []
        )

        cache_key = self._get_cache_key(prompt)
        if cache_key in self._cache and self._is_cache_valid(self._cache[cache_key][1]):
            logger.info("Cache hit for question generation")
            return self._cache[cache_key][0]

        start_time = time.time()

        for attempt in range(self.max_retries):
            try:
                parsed = self._structured_generate(prompt, QuestionSchema)
                if parsed:
                    latency = time.time() - start_time
                    self._update_metrics(None, latency, student_id)

                    question = Question(
                        id=f"q_{int(time.time())}_{hash(parsed.question) % 100000}",
                        question=parsed.question,
                        answer=parsed.answer,
                        topic=topic,
                        difficulty=round(parsed.difficulty, 1),
                        options=parsed.options,
                        explanation=parsed.explanation,
                        estimated_time=parsed.estimated_time,
                        concept_focus=parsed.concept_focus,
                        hint=parsed.hint,
                        source="groq"
                    )

                    # Cache the result
                    self._cache[cache_key] = (question, time.time())
                    return question

            except RateLimitError:
                wait = (2 ** attempt) * 2.5
                logger.warning(f"Rate limit hit. Waiting {wait:.1f}s...")
                time.sleep(wait)
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed: {e}")
                time.sleep(1.2)

        logger.error("All retries failed. Returning fallback MCQ.")
        return self._fallback_mcq_question(topic, target_difficulty)

    def _build_mcq_prompt(self, topic: str, target_difficulty: float, 
                          focus_topic: Optional[str], trickiness: float,
                          learning_mode: str, weak_topics: List[str]) -> str:
        """Force MCQ format with high quality"""
        difficulty_text = {1:"very easy", 2:"easy", 3:"medium", 4:"hard", 5:"expert"}.get(int(target_difficulty), "medium")

        prompt = f"""You are an expert Computer Science tutor.

Generate **exactly ONE** high-quality MCQ question.

Topic: {topic}
Focus: {focus_topic or 'core concepts'}
Difficulty: {target_difficulty:.1f}/5.0 → {difficulty_text}
Trickiness: {"straightforward" if trickiness < 0.3 else "moderately tricky" if trickiness < 0.7 else "highly tricky with conceptual traps"}
Weak Topics: {', '.join(weak_topics) if weak_topics else 'none'}

Requirements:
- Must be Multiple Choice with **exactly 4 options** (A, B, C, D)
- Only ONE correct answer
- Make distractors realistic and educational
- Include a short optional hint

Respond **only** with valid JSON:
{{
  "question": "The full question text",
  "answer": "Correct option letter (A/B/C/D)",
  "options": ["A. text", "B. text", "C. text", "D. text"],
  "explanation": "Clear educational explanation",
  "difficulty": {target_difficulty:.1f},
  "estimated_time": 30,
  "concept_focus": "Main concept",
  "hint": "Optional short hint for student"
}}

JSON only. No extra text."""

        return prompt.strip()

    def _structured_generate(self, prompt: str, schema: type[BaseModel]) -> Optional[BaseModel]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a precise JSON-only responder."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content.strip()
        parsed = schema.model_validate_json(content)
        return parsed

    def _fallback_mcq_question(self, topic: str, difficulty: float) -> Question:
        return Question(
            id=f"fallback_{int(time.time())}",
            question=f"What is a fundamental concept in {topic}?",
            answer="A",
            topic=topic,
            difficulty=round(difficulty, 1),
            options=[
                "A. Correct foundational answer",
                "B. Common misconception",
                "C. Plausible but incorrect",
                "D. Another distractor"
            ],
            explanation="This is a safe fallback MCQ.",
            estimated_time=20,
            hint="Think about basic definitions."
        )

    # =============================================================
    # ADDITIONAL FEATURES
    # =============================================================
    def generate_explanation(self, question: str, student_answer: str, correct_answer: str) -> str:
        """Generate personalized explanation"""
        prompt = f"""Explain this to a student:

Question: {question}
Student Answer: {student_answer}
Correct Answer: {correct_answer}

Be encouraging, clear, and educational."""
        return self.generate(prompt, temperature=0.7)

    def health_check(self) -> bool:
        try:
            resp = self.generate("Say only the word OK")
            return "OK" in resp.upper()
        except:
            return False

    def switch_model(self, new_model: str):
        self.model = new_model
        self._cache.clear()
        logger.info(f"Switched LLM model to: {new_model}")

    def clear_cache(self):
        self._cache.clear()
        logger.info("LLM cache cleared.")

    def get_usage_stats(self, student_id: Optional[str] = None) -> Dict:
        avg_latency = self.total_latency / self.total_requests if self.total_requests > 0 else 0
        return {
            "total_requests": self.total_requests,
            "total_tokens_used": self.total_tokens_used,
            "avg_latency_seconds": round(avg_latency, 3),
            "estimated_cost_usd": round(self.cost_tracker.get(student_id, 0), 6) if student_id else sum(self.cost_tracker.values())
        }


# Backward compatibility
    def generate(self, prompt: str, temperature: Optional[float] = None) -> str:
        temp = temperature or self.temperature
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temp,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return "Sorry, I couldn't generate a response right now."