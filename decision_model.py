# core/engine/decision_model.py

import random
import time
from typing import Dict, List, Any, Optional
from collections import defaultdict
import logging
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DecisionOutput:
    action: str
    recommended_difficulty: float
    trickiness: float
    focus_topic: str
    learning_mode: str
    next_strategy: str
    explanation: str
    confidence_calibration: Dict[str, float]
    suggested_time_per_question: int


class DecisionModel:
    def __init__(self):
        self.student_profiles: Dict[str, Dict] = {}
        self.decision_history: Dict[str, List] = defaultdict(list)

    # =============================================================
    # MAIN DECISION ENTRY POINT
    # =============================================================
    def decide(self, student_id: str, engine_summary: Dict, current_question: Optional[Any] = None) -> DecisionOutput:
        """
        Takes summary from AdaptiveEngine.get_summary() and returns smart decisions.
        """
        profile = self._get_or_create_profile(student_id, engine_summary)
        
        # Multi-factor analysis
        performance = self._analyze_performance(engine_summary, profile)
        behavior = self._predict_behavior(engine_summary, profile)
        cognitive_state = self._detect_cognitive_state(engine_summary, profile)
        engagement = self._assess_engagement(engine_summary, profile)
        
        # Advanced decision making
        strategy = self._select_strategy(performance, behavior, cognitive_state, engagement)
        difficulty = self._control_difficulty(engine_summary, strategy, profile)
        trickiness = self._decide_trickiness(behavior, performance, cognitive_state)
        
        focus_topic = self._focus_topic(engine_summary, profile)
        learning_mode = self._determine_learning_mode(engine_summary, profile)
        next_strategy = self._suggest_next_strategy(strategy, focus_topic)

        # Confidence calibration & explanation
        calibration = self._calibrate_confidence(engine_summary, profile)
        explanation = self._generate_decision_explanation(
            strategy, difficulty, trickiness, focus_topic, performance, behavior
        )

        decision = DecisionOutput(
            action=strategy,
            recommended_difficulty=round(difficulty, 2),
            trickiness=round(trickiness, 2),
            focus_topic=focus_topic,
            learning_mode=learning_mode,
            next_strategy=next_strategy,
            explanation=explanation,
            confidence_calibration=calibration,
            suggested_time_per_question=self._suggest_time_per_question(difficulty, behavior)
        )

        self._log_decision(student_id, decision, engine_summary)
        
        logger.info(f"Decision for {student_id}: {strategy} | Diff: {difficulty:.2f} | Focus: {focus_topic}")
        return decision

    # =============================================================
    # PROFILE MANAGEMENT
    # =============================================================
    def _get_or_create_profile(self, student_id: str, summary: Dict) -> Dict:
        if student_id not in self.student_profiles:
            self.student_profiles[student_id] = {
                "history": [],
                "topic_mastery": defaultdict(lambda: {"mastery": 0.5, "last_practiced": time.time(), "attempts": 0}),
                "avg_response_time": 25.0,
                "confidence_history": [],
                "learning_style": "analytical",
                "burnout_risk": 0.0,
                "momentum": 1.0,
                "total_decisions": 0
            }

        profile = self.student_profiles[student_id]
        profile["history"].append(summary)
        if len(profile["history"]) > 50:
            profile["history"] = profile["history"][-50:]

        self._apply_forgetting_curve(profile)
        return profile

    def _apply_forgetting_curve(self, profile: Dict):
        current_time = time.time()
        for topic, data in profile["topic_mastery"].items():
            days_since = (current_time - data["last_practiced"]) / 86400
            if days_since > 3:
                decay = 0.92 ** days_since
                data["mastery"] = max(0.15, data["mastery"] * decay)

    # =============================================================
    # ANALYSIS LAYERS
    # =============================================================
    def _analyze_performance(self, summary: Dict, profile: Dict) -> str:
        accuracy = summary.get("accuracy", 50) / 100
        elo = summary.get("elo_rating", 1000)
        difficulty = summary.get("current_difficulty", 2.0)
        normalized_elo = (elo - 600) / 1200

        if accuracy > 0.85 and difficulty > 3.5 and normalized_elo > 0.7:
            return "excellent"
        elif accuracy > 0.75:
            return "strong"
        elif accuracy > 0.55:
            return "average"
        else:
            return "weak"

    def _predict_behavior(self, summary: Dict, profile: Dict) -> str:
        accuracy = summary.get("accuracy", 50) / 100
        streak = summary.get("streak", 0)
        weak_topics = summary.get("weak_topics", [])

        if len(weak_topics) >= 3:
            return "struggling"
        elif streak >= 5 and accuracy > 0.85:
            return "confident"
        elif accuracy < 0.4:
            return "frustrated"
        elif streak == 0 and accuracy < 0.6:
            return "inconsistent"
        return "steady"

    def _detect_cognitive_state(self, summary: Dict, profile: Dict) -> str:
        accuracy = summary.get("accuracy", 50) / 100
        burnout_risk = profile["burnout_risk"]

        if accuracy < 0.35 or burnout_risk > 0.7:
            return "burnout_risk"
        elif accuracy > 0.92:
            return "flow_state"
        elif 0.75 < accuracy < 0.92:
            return "optimal"
        return "stable"

    def _assess_engagement(self, summary: Dict, profile: Dict) -> float:
        streak = summary.get("streak", 0)
        accuracy = summary.get("accuracy", 50) / 100
        return min(1.0, (streak * 0.12) + (accuracy * 0.6) + 0.2)

    # =============================================================
    # DECISION LOGIC
    # =============================================================
    def _select_strategy(self, perf: str, behavior: str, state: str, engagement: float) -> str:
        if state == "burnout_risk":
            return "recovery_mode"
        if behavior == "struggling":
            return "weakness_rebuild"
        if perf == "excellent" and engagement > 0.85:
            return "challenge_mode"
        if behavior == "confident" and perf in ["strong", "excellent"]:
            return "deep_dive"
        if behavior == "frustrated":
            return "motivation_boost"
        if perf == "weak":
            return "scaffolded_learning"
        
        strategies = ["spaced_practice", "mixed_review", "concept_reinforcement"]
        return random.choices(strategies, weights=[0.4, 0.35, 0.25])[0]

    def _control_difficulty(self, summary: Dict, strategy: str, profile: Dict) -> float:
        current_diff = summary.get("current_difficulty", 2.0)
        momentum = profile["momentum"]

        adjustments = {
            "challenge_mode": +0.8,
            "deep_dive": +0.6,
            "weakness_rebuild": -0.9,
            "recovery_mode": -1.2,
            "scaffolded_learning": -0.5,
            "motivation_boost": -0.3,
        }

        adjustment = adjustments.get(strategy, 0.0)
        new_diff = current_diff + adjustment * momentum
        new_diff += random.uniform(-0.3, 0.3)
        return max(1.0, min(5.0, new_diff))

    def _decide_trickiness(self, behavior: str, perf: str, state: str) -> float:
        if behavior == "confident" and perf in ["strong", "excellent"] and state == "flow_state":
            return 0.85
        if behavior == "struggling" or state == "burnout_risk":
            return 0.15
        if behavior == "steady":
            return 0.45
        return 0.6

    def _focus_topic(self, summary: Dict, profile: Dict) -> str:
        weak_topics = summary.get("weak_topics", [])
        if weak_topics:
            return min(weak_topics, key=lambda t: profile["topic_mastery"][t]["mastery"])
        return summary.get("topic", "general")

    def _determine_learning_mode(self, summary: Dict, profile: Dict) -> str:
        accuracy = summary.get("accuracy", 50) / 100
        if accuracy > 0.88:
            return "mastery_mode"
        elif accuracy > 0.70:
            return "exam_simulation"
        elif accuracy < 0.45:
            return "foundational_learning"
        return "adaptive_practice"

    def _suggest_next_strategy(self, current_strategy: str, focus_topic: str) -> str:
        mapping = {
            "weakness_rebuild": "spaced_repetition",
            "challenge_mode": "concept_application",
            "recovery_mode": "gamified_review",
            "deep_dive": "real_world_scenario"
        }
        return mapping.get(current_strategy, "mixed_practice")

    def _calibrate_confidence(self, summary: Dict, profile: Dict) -> Dict:
        accuracy = summary.get("accuracy", 50) / 100
        return {
            "student_reported": summary.get("confidence", 0.5),
            "actual": accuracy,
            "calibration_gap": abs(accuracy - summary.get("confidence", 0.5)),
            "recommendation": "overconfident" if accuracy < 0.6 else "well_calibrated"
        }

    def _suggest_time_per_question(self, difficulty: float, behavior: str) -> int:
        base = int(15 + difficulty * 12)
        if behavior in ["struggling", "frustrated"]:
            base = int(base * 1.25)
        return max(20, min(90, base))

    def _generate_decision_explanation(self, strategy: str, diff: float, trick: float,
                                       focus: str, perf: str, behavior: str) -> str:
        reasons = []
        if strategy == "weakness_rebuild":
            reasons.append(f"Student is weak in {focus}")
        if diff < 2.0:
            reasons.append("Lowering difficulty to build confidence")
        if trick > 0.7:
            reasons.append("Adding conceptual traps to test deeper understanding")
        
        return f"Strategy: {strategy}. " + " | ".join(reasons) if reasons else "Balanced adaptive practice."

    def _log_decision(self, student_id: str, decision: DecisionOutput, summary: Dict):
        self.decision_history[student_id].append({
            "timestamp": time.time(),
            "decision": asdict(decision),
            "summary_accuracy": summary.get("accuracy")
        })
        if len(self.decision_history[student_id]) > 100:
            self.decision_history[student_id] = self.decision_history[student_id][-100:]

    # =============================================================
    # PUBLIC UTILITIES
    # =============================================================
    def get_profile(self, student_id: str) -> Optional[Dict]:
        return self.student_profiles.get(student_id)

    def reset_profile(self, student_id: str):
        if student_id in self.student_profiles:
            del self.student_profiles[student_id]