# core/ai/prompt_engineering.py

from typing import List, Optional, Dict, Any


class PromptEngine:
    """
    Advanced Prompt Engineering System for Adaptive Learning.
    Highly strict, structured, and optimized for Groq LLM + AdaptiveEngine.
    """

    def __init__(self):
        self.system_rules = """
You are an expert Computer Science tutor specializing in adaptive learning for students.

STRICT MANDATORY RULES (Never break these):
1. Generate ONLY Computer Science related questions. Never generate math, physics, or general knowledge questions.
2. Questions must be clear, concise, and age-appropriate for school/college students.
3. Strictly follow the requested difficulty level.
4. Always respond in valid JSON format only. No extra text, no explanations, no greetings.
5. Never add "Sure", "Here is", "According to", or any conversational filler.
6. Avoid ambiguity and tricky wording unless explicitly requested.
7. For MCQ questions, provide exactly 4 options with only ONE correct answer.
"""

    # =============================================================
    # ADVANCED QUESTION PROMPT (Strict + Structured)
    # =============================================================
    def generate_question_prompt(
        self,
        topic: str,
        difficulty: float,
        trickiness: float = 0.4,
        focus_topic: Optional[str] = None,
        student_weak_topics: Optional[List[str]] = None,
        learning_mode: str = "adaptive_practice"
    ) -> str:
        """
        Creates a highly controlled prompt for Groq to generate structured questions.
        """

        diff_desc = {
            1.0: "very easy (basic recall)",
            2.0: "easy (simple understanding)",
            3.0: "medium (standard application)",
            4.0: "hard (deep analysis)",
            5.0: "expert (complex scenarios and edge cases)"
        }

        difficulty_text = diff_desc.get(round(difficulty), "medium")

        trick_desc = "straightforward and clear" if trickiness < 0.3 else \
                     "moderately tricky with common misconceptions" if trickiness < 0.7 else \
                     "highly tricky with subtle conceptual traps"

        weak_text = ", ".join(student_weak_topics) if student_weak_topics else "none"

        focus = focus_topic or "core concepts"

        prompt = f"""You are an expert Computer Science tutor.

{self.system_rules}

Generate **exactly ONE** high-quality Computer Science question.

Topic: {topic}
Focus Area: {focus}
Difficulty Level: {difficulty:.1f}/5.0 → {difficulty_text}
Trickiness: {trick_desc}
Learning Mode: {learning_mode}
Student's Weak Topics: {weak_text}

Requirements:
- Question must be directly related to {topic}.
- Make it engaging but educational.
- If suitable, make it multiple choice with 4 options (A, B, C, D).
- Keep question concise (max 2 lines).

Respond **only** with a valid JSON object using this exact schema:

{{
  "question": "The full question text here",
  "answer": "The correct answer as string",
  "options": ["Option A text", "Option B text", "Option C text", "Option D text"] or null,
  "explanation": "Clear, educational explanation of why the answer is correct",
  "difficulty": {difficulty:.1f},
  "estimated_time": 30,
  "concept_focus": "Short name of the main concept being tested"
}}

Generate only the JSON. No other text whatsoever.
"""

        return prompt.strip()

    # =============================================================
    # EXPLANATION / FEEDBACK PROMPT
    # =============================================================
    def generate_explanation_prompt(
        self,
        question: str,
        student_answer: str,
        correct_answer: str,
        student_level: str = "intermediate"
    ) -> str:
        """Generates a personalized, encouraging explanation."""

        prompt = f"""You are a patient and encouraging Computer Science tutor.

Explain the following to a student at {student_level} level.

Question: {question}
Student's Answer: {student_answer}
Correct Answer: {correct_answer}

Rules for explanation:
- Be kind, supportive and motivating.
- Clearly explain why the correct answer is right.
- Gently point out the mistake if student was wrong.
- Use simple language.
- Keep the explanation short and structured (3-6 sentences max).
- End with a positive note or learning tip.

Explanation:"""

        return prompt.strip()

    # =============================================================
    # FULL PROMPT BUILDER (Main Entry Point)
    # =============================================================
    def build_prompt(
        self,
        mode: str = "question",
        topic: str = "Programming",
        difficulty: float = 2.5,
        trickiness: float = 0.45,
        focus_topic: Optional[str] = None,
        student_weak_topics: Optional[List[str]] = None,
        learning_mode: str = "adaptive_practice",
        question: str = "",
        student_answer: str = "",
        correct_answer: str = "",
        student_level: str = "intermediate"
    ) -> str:
        """
        Unified prompt builder compatible with AdaptiveEngine + LLMGroq.
        """
        if mode == "question":
            return self.generate_question_prompt(
                topic=topic,
                difficulty=difficulty,
                trickiness=trickiness,
                focus_topic=focus_topic,
                student_weak_topics=student_weak_topics,
                learning_mode=learning_mode
            )

        elif mode == "explanation":
            return self.generate_explanation_prompt(
                question=question,
                student_answer=student_answer,
                correct_answer=correct_answer,
                student_level=student_level
            )

        else:
            raise ValueError(f"Unsupported prompt mode: {mode}")

    # =============================================================
    # HELPER METHODS
    # =============================================================
    def get_system_rules(self) -> str:
        """Return base system rules for debugging or system messages."""
        return self.system_rules.strip()