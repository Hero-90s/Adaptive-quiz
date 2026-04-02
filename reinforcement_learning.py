import random
import time
from collections import defaultdict, deque
from typing import Dict, Any, Tuple, List, Optional
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReinforcementModel:
    """
    Advanced Reinforcement Learning module for Adaptive Learning System.
    Uses Q-Learning with experience replay, double Q-learning style stability,
    and rich state representation compatible with AdaptiveEngine + DecisionModel.
    """

    def __init__(self):
        # Per-student Q-tables: student_id -> state -> strategy -> value
        self.q_tables: Dict[str, Dict[Tuple, Dict[str, float]]] = defaultdict(
            lambda: defaultdict(lambda: {
                "practice_mode": 0.0,
                "challenge_mode": 0.0,
                "recovery_mode": 0.0,
                "weakness_rebuild": 0.0,
                "deep_dive": 0.0,
                "spaced_practice": 0.0,
                "scaffolded_learning": 0.0,
                "motivation_boost": 0.0,
            })
        )

        # Experience replay buffer (for stability)
        self.replay_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))

        # Tracking
        self.strategy_usage: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.history: Dict[str, List[Dict]] = defaultdict(list)

        # Hyperparameters (adaptive)
        self.epsilon: Dict[str, float] = defaultdict(lambda: 0.35)      # exploration
        self.epsilon_decay = 0.985
        self.epsilon_min = 0.08

        self.alpha = 0.12               # learning rate (lower = more stable)
        self.gamma = 0.92               # discount factor

        self.min_reward = -15.0
        self.max_reward = 25.0

    # =============================================================
    # 1. RICH STATE REPRESENTATION (Compatible with AdaptiveEngine)
    # =============================================================
    def _get_state(self, summary: Dict) -> Tuple:
        """
        Creates a rich, hashable state from engine summary + decision context.
        """
        accuracy_bucket = int(summary.get("accuracy", 50) // 10)          # 0-10
        difficulty_bucket = int(summary.get("current_difficulty", 2.0))
        elo_bucket = int((summary.get("elo_rating", 1000) - 600) // 200)  # 0-6 roughly
        streak_bucket = min(5, summary.get("streak", 0) // 2)
        weak_count = len(summary.get("weak_topics", []))

        # Engagement proxy
        engagement = summary.get("engagement_score", 0.5)

        # Make state hashable
        return (
            accuracy_bucket,
            difficulty_bucket,
            elo_bucket,
            streak_bucket,
            weak_count,
            round(engagement, 1)
        )

    # =============================================================
    # 2. CHOOSE STRATEGY (Exploration + DecisionModel hint)
    # =============================================================
    def choose_strategy(self, student_id: str, decision_output: Any, summary: Dict) -> str:
        """
        Uses DecisionModel suggestion as prior, but applies RL exploration.
        Fully compatible with DecisionOutput from DecisionModel.
        """
        state = self._get_state(summary)
        q_table = self.q_tables[student_id]

        # Get hint from DecisionModel
        suggested_action = getattr(decision_output, "action", "practice_mode")

        if random.random() < self.epsilon[student_id]:
            # Exploration
            strategy = random.choice(list(q_table[state].keys()))
            logger.debug(f"RL Exploration → Strategy: {strategy}")
        else:
            # Exploitation with bias toward DecisionModel suggestion
            if suggested_action in q_table[state] and q_table[state][suggested_action] > -5:
                strategy = suggested_action
            else:
                # Fallback to best known for this state
                strategy = max(q_table[state], key=q_table[state].get)

        self.strategy_usage[student_id][strategy] += 1
        return strategy

    # =============================================================
    # 3. ADVANCED REWARD FUNCTION
    # =============================================================
    def _calculate_reward(self, prev_summary: Dict, new_summary: Dict, strategy: str) -> float:
        """Multi-factor reward combining performance, progress, and engagement."""
        score_diff = new_summary.get("score", 0) - prev_summary.get("score", 0)
        acc_diff = new_summary.get("accuracy", 50) - prev_summary.get("accuracy", 50)
        
        difficulty_progress = new_summary.get("current_difficulty", 2.0) - prev_summary.get("current_difficulty", 2.0)
        
        # Streak & engagement bonus
        streak_bonus = min(8, new_summary.get("streak", 0) * 1.2)
        engagement_bonus = (new_summary.get("engagement_score", 0.5) - 0.4) * 12

        # Weak topic improvement bonus
        weak_improvement = 0.0
        if prev_summary.get("weak_topics") and not new_summary.get("weak_topics"):
            weak_improvement = 15.0

        reward = (
            score_diff * 1.8 +
            acc_diff * 0.9 +
            difficulty_progress * 4.5 +
            streak_bonus +
            engagement_bonus +
            weak_improvement
        )

        # Heavy penalty for burnout / big drops
        if acc_diff < -12:
            reward -= 18
        if new_summary.get("streak", 0) == 0 and acc_diff < -5:
            reward -= 10

        # Clip for stability
        reward = max(self.min_reward, min(self.max_reward, reward))
        return round(reward, 2)

    # =============================================================
    # 4. Q-LEARNING UPDATE WITH EXPERIENCE REPLAY
    # =============================================================
    def update(self, student_id: str, prev_summary: Dict, new_summary: Dict, strategy: str):
        """Update Q-values using experience replay for better stability."""
        prev_state = self._get_state(prev_summary)
        new_state = self._get_state(new_summary)

        reward = self._calculate_reward(prev_summary, new_summary, strategy)

        q_table = self.q_tables[student_id]

        # Double Q-learning style (use max of current table)
        old_q = q_table[prev_state][strategy]
        max_future_q = max(q_table[new_state].values()) if q_table[new_state] else 0.0

        # Q-update
        new_q = old_q + self.alpha * (reward + self.gamma * max_future_q - old_q)
        q_table[prev_state][strategy] = round(new_q, 4)

        # Store experience for replay
        self.replay_buffer[student_id].append({
            "prev_state": prev_state,
            "strategy": strategy,
            "reward": reward,
            "new_state": new_state
        })

        # Occasional replay update (mini-batch style)
        if len(self.replay_buffer[student_id]) >= 8:
            self._replay_update(student_id)

        # Decay exploration
        if self.epsilon[student_id] > self.epsilon_min:
            self.epsilon[student_id] *= self.epsilon_decay

        # Log history
        self.history[student_id].append({
            "timestamp": time.time(),
            "state": prev_state,
            "strategy": strategy,
            "reward": reward,
            "new_q": new_q,
            "epsilon": self.epsilon[student_id]
        })

        if len(self.history[student_id]) > 200:
            self.history[student_id] = self.history[student_id][-200:]

    def _replay_update(self, student_id: str):
        """Sample from replay buffer and update Q-values (improves stability)."""
        q_table = self.q_tables[student_id]
        batch = random.sample(list(self.replay_buffer[student_id]), min(6, len(self.replay_buffer[student_id])))

        for exp in batch:
            old_q = q_table[exp["prev_state"]][exp["strategy"]]
            max_future = max(q_table[exp["new_state"]].values()) if q_table[exp["new_state"]] else 0.0

            new_q = old_q + self.alpha * 0.7 * (exp["reward"] + self.gamma * max_future - old_q)
            q_table[exp["prev_state"]][exp["strategy"]] = round(new_q, 4)

    # =============================================================
    # 5. UTILITY METHODS
    # =============================================================
    def get_best_strategy_for_state(self, student_id: str, summary: Dict) -> str:
        """Get the current best strategy for a given state."""
        state = self._get_state(summary)
        q_table = self.q_tables[student_id][state]
        if not q_table:
            return "practice_mode"
        return max(q_table, key=q_table.get)

    def get_global_best_strategy(self, student_id: str) -> str:
        """Overall best performing strategy across all states for this student."""
        combined = defaultdict(float)
        q_table = self.q_tables[student_id]

        for state_strategies in q_table.values():
            for strat, val in state_strategies.items():
                combined[strat] += val

        if not combined:
            return "practice_mode"
        return max(combined, key=combined.get)

    def get_learning_stats(self, student_id: str) -> Dict:
        """Return useful debugging and monitoring stats."""
        total_decisions = sum(self.strategy_usage[student_id].values())
        if total_decisions == 0:
            return {"status": "No data yet"}

        return {
            "total_decisions": total_decisions,
            "strategy_distribution": dict(self.strategy_usage[student_id]),
            "current_epsilon": round(self.epsilon[student_id], 3),
            "best_strategy": self.get_global_best_strategy(student_id),
            "recent_rewards": [h["reward"] for h in self.history[student_id][-10:]],
            "avg_reward": round(sum(h["reward"] for h in self.history[student_id][-20:]) / 20, 2) 
                         if len(self.history[student_id]) >= 20 else 0.0
        }

    def reset_student(self, student_id: str):
        """Reset RL data for a specific student."""
        if student_id in self.q_tables:
            del self.q_tables[student_id]
        if student_id in self.replay_buffer:
            del self.replay_buffer[student_id]
        self.epsilon[student_id] = 0.35

    def save_q_table(self, filepath: str = "database/rl_qtable.json"):
        """Optional: Save Q-table for persistence (simple JSON)."""
        try:
            data = {sid: {str(k): v for k, v in table.items()} for sid, table in self.q_tables.items()}
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            logger.info("Q-table saved successfully")
        except Exception as e:
            logger.warning(f"Failed to save Q-table: {e}")

    def load_q_table(self, filepath: str = "database/rl_qtable.json"):
        """Optional: Load Q-table."""
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            # Note: Full reconstruction would need tuple conversion - simplified for now
            logger.info("Q-table loaded (partial)")
        except FileNotFoundError:
            logger.info("No saved Q-table found. Starting fresh.")