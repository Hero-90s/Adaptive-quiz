# core/ai/response_optimizer.py
import random
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from Core.Engine.adaptive_engine import Question
from .prompt_engineering import PromptEngine

@dataclass
class OptimizedResponse:
    """Clean, structured response that the frontend can easily consume."""
    message: str                    # Final polite & encouraging text
    explanation: Optional[str] = None
    tip: Optional[str] = None
    motivation: Optional[str] = None
    follow_up_suggestion: Optional[str] = None
    emoji: Optional[str] = None
    tone: str = "encouraging"       # encouraging | supportive | gentle | celebratory


class ResponseOptimizer:
    """
    Advanced Response Optimizer for Adaptive Learning System.
    Makes every answer respectful, encouraging, child-friendly,
    and pedagogically perfect.
    """

    def __init__(self):
        self.prompt_engine = PromptEngine()

        # Reusable positive templates
        self.positive_templates = [
            "Great job!",
            "You're doing awesome!",
            "Fantastic effort!",
            "You're getting better every time!",
            "Excellent work!",
            "I'm really proud of you!",
            "Keep shining like this!",
        ]

        self.gentle_correction_templates = [
            "No worries, we all learn from mistakes!",
            "That's a common mix-up, let me help you understand.",
            "You're very close! Let's look at it together.",
            "Small step back, big leap forward!",
        ]

        self.motivation_db = [
            "Every correct answer makes you stronger!",
            "Consistency beats talent every single day.",
            "You're building a superpower called knowledge.",
            "One question at a time, you're becoming unstoppable.",
        ]

    # =============================================================
    # 1. MAIN OPTIMIZER (Most Important Method)
    # =============================================================
    def optimize(
        self,
        raw_explanation: str,
        question: Question,
        student_answer: str,
        is_correct: bool,
        student_id: str,
        summary: Dict,
        decision: Optional[Any] = None,
    ) -> OptimizedResponse:
        """
        Takes raw LLM output and returns a perfectly polished,
        respectful, and motivating response.
        """
        student_level = summary.get("accuracy", 50) > 70 and "intermediate" or "beginner"

        # Base polite explanation
        explanation = self._make_respectful_explanation(
            raw_explanation, question, student_answer, is_correct, student_level
        )

        # Add motivational layer
        motivation = self._generate_motivation(is_correct, summary)

        # Add learning tip
        tip = self._generate_learning_tip(question, is_correct)

        # Optional follow-up suggestion
        follow_up = self._suggest_next_step(decision, question.topic) if decision else None

        # Choose appropriate emoji
        emoji = self._choose_emoji(is_correct, summary.get("streak", 0))

        return OptimizedResponse(
            message=self._build_final_message(is_correct, summary),
            explanation=explanation,
            tip=tip,
            motivation=motivation,
            follow_up_suggestion=follow_up,
            emoji=emoji,
            tone="celebratory" if is_correct and summary.get("streak", 0) >= 3 else "encouraging"
        )

    # =============================================================
    # 2. CORE HELPERS (15+ Advanced Features Built-in)
    # =============================================================
    def _make_respectful_explanation(
        self,
        raw: str,
        question: Question,
        student_answer: str,
        is_correct: bool,
        student_level: str
    ) -> str:
        """Feature 1-5: Politeness + Gentle correction + Clarity"""
        if is_correct:
            prefix = random.choice(self.positive_templates) + " "
            return prefix + raw.strip()

        # Gentle correction for wrong answers
        correction = random.choice(self.gentle_correction_templates)
        prompt = self.prompt_engine.generate_explanation_prompt(
            question=question.question,
            student_answer=student_answer,
            correct_answer=question.answer,
            student_level=student_level
        )

        # In real usage you can call LLMGroq here for re-generation
        # For speed we return a polite version
        return f"{correction}\n\n{raw.strip()}"

    def _generate_motivation(self, is_correct: bool, summary: Dict) -> str:
        """Feature 6-8: Personalized motivation + streak awareness"""
        streak = summary.get("streak", 0)
        if streak >= 5:
            return f"🔥 {streak}-question streak! You're on fire today!"
        if is_correct:
            return random.choice(self.motivation_db)
        return "Every mistake is a step closer to mastery. You've got this!"

    def _generate_learning_tip(self, question: Question, is_correct: bool) -> Optional[str]:
        """Feature 9: Smart learning tip"""
        if not question.explanation:
            return None
        tips = [
            "Pro tip: Try explaining this concept in your own words.",
            "Remember: Practice makes permanent!",
            "Challenge: Can you teach this to a friend?",
            "Next level: Try solving a harder version of this.",
        ]
        return random.choice(tips)

    def _suggest_next_step(self, decision: Any, current_topic: str) -> Optional[str]:
        """Feature 10: Intelligent next-step suggestion"""
        if not decision:
            return None
        if getattr(decision, "action", "") == "weakness_rebuild":
            return f"Would you like to practice more on {current_topic}?"
        if getattr(decision, "action", "") == "challenge_mode":
            return "Ready for a slightly harder question?"
        return None

    def _choose_emoji(self, is_correct: bool, streak: int) -> str:
        """Feature 11: Age-appropriate emoji control"""
        if streak >= 4:
            return "🔥" if is_correct else "💪"
        return "✅" if is_correct else "🌱"

    def _build_final_message(self, is_correct: bool, summary: Dict) -> str:
        """Feature 12: Final encouraging wrapper"""
        accuracy = summary.get("accuracy", 50)
        if is_correct and accuracy > 80:
            return "Brilliant! You're mastering this topic!"
        if is_correct:
            return "Correct! Well done!"
        return "Let's learn from this together!"

    # =============================================================
    # 13. BULK OPTIMIZATION (for summaries, leaderboards, etc.)
    # =============================================================
    def optimize_summary(self, summary: Dict) -> Dict:
        """Feature 13: Polished session summary"""
        score = summary.get("score", 0)
        if score >= 85:
            tone = "You're a star! 🌟"
        elif score >= 70:
            tone = "Solid performance! Keep going!"
        else:
            tone = "Every session makes you better. Proud of you!"

        return {
            **summary,
            "encouraging_message": tone,
            "motivational_tip": random.choice(self.motivation_db),
            "emoji": "🏆" if score >= 85 else "👍"
        }

    # =============================================================
    # 14. LEADERBOARD & SOCIAL RESPONSE
    # =============================================================
    def generate_leaderboard_message(self, rank: str, student_id: str) -> str:
        """Feature 14: Respectful leaderboard feedback"""
        messages = {
            "Emperor 👑": f"Legendary performance, {student_id}! You're at the very top!",
            "Diamond": "Diamond league! Incredible consistency!",
            "Platinum": "Platinum rank achieved! You're in elite company.",
            "Gold": "Gold medalist! Amazing job!",
            "Silver": "Silver rank! You're so close to the top!",
            "Bronze": "Bronze secured! Every step counts.",
        }
        return messages.get(rank, "Great effort! Keep climbing the leaderboard!")

    # =============================================================
    # 15. VOICE-FRIENDLY + SPEECH OPTIMIZATION
    # =============================================================
    def make_speech_friendly(self, text: str) -> str:
        """Feature 15: Clean text for text-to-speech"""
        text = text.replace("✅", "").replace("🔥", "").replace("🌟", "")
        return text.strip()

    # =============================================================
    # 16. BONUS: Quick motivational one-liner (used anywhere)
    # =============================================================
    def quick_motivate(self, streak: int = 0) -> str:
        """Feature 16: Instant motivation"""
        if streak >= 5:
            return f"🔥 {streak} in a row! You're unstoppable!"
        return random.choice(self.positive_templates)

    # =============================================================
    # 17. FULL RESPONSE PIPELINE (Recommended usage)
    # =============================================================
    def process_llm_response(
        self,
        raw_response: str,
        question: Question,
        student_answer: str,
        is_correct: bool,
        student_id: str,
        summary: Dict,
        decision: Optional[Any] = None,
    ) -> OptimizedResponse:
        """One-call pipeline – use this everywhere."""
        return self.optimize(
            raw_explanation=raw_response,
            question=question,
            student_answer=student_answer,
            is_correct=is_correct,
            student_id=student_id,
            summary=summary,
            decision=decision
        )