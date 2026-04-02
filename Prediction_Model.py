import numpy as np
from collections import deque

class PredictionModel:

    def __init__(self):
        self.history = {}
        self.window_size = 10   # recent memory

    # -------------------------------
    # STORE HISTORY
    # -------------------------------
    def update_history(self, student_id, summary):
        if student_id not in self.history:
            self.history[student_id] = deque(maxlen=self.window_size)

        self.history[student_id].append(summary)

    # -------------------------------
    # FEATURE EXTRACTION (20+ FEATURES)
    # -------------------------------
    def extract_features(self, student_id, summary):

        hist = self.history.get(student_id, [])
        
        scores = [h["score"] for h in hist]
        accuracies = [h["accuracy"] for h in hist]

        # 📊 Basic
        score = summary["score"]
        accuracy = summary["accuracy"]
        iq = summary["iq"]
        total = summary["total"]
        correct = summary["correct"]
        wrong = total - correct

        # 📈 Trends
        score_trend = np.mean(np.diff(scores)) if len(scores) > 1 else 0
        acc_trend = np.mean(np.diff(accuracies)) if len(accuracies) > 1 else 0

        # 🧠 Behavior
        weak_count = len(summary["weak_topic"])
        consistency = np.std(scores) if len(scores) > 1 else 0

        # 🔥 Advanced engineered features
        error_rate = wrong / max(1, total)
        improvement_rate = score_trend
        confidence = accuracy / 100
        retention = correct / max(1, total)
        adaptability = iq / 160

        fatigue = max(0, (len(hist) - 5) * 0.1)  # longer session = fatigue

        return np.array([
            score, accuracy, iq,
            total, correct, wrong,
            score_trend, acc_trend,
            weak_count, consistency,
            error_rate, improvement_rate,
            confidence, retention,
            adaptability, fatigue
        ])

    # -------------------------------
    # PREDICT FUTURE SCORE
    # -------------------------------
    def predict_score(self, features):
       weights = [
            0.4, 0.5, 0.1,   # increase score + accuracy
            0.05, 0.05, -0.02,
            0.2, 0.1,
            -0.05, -0.02,
            -0.1, 0.3,
            0.2, 0.2,
            0.1, -0.05
        ]
       
       prediction = np.dot(features, weights) / 2
       return max(0, min(100, prediction))

    # -------------------------------
    # FAILURE RISK
    # -------------------------------
    def predict_failure_risk(self, features):
        risk = 0

        if features[1] < 50:  # accuracy
            risk += 0.4
        if features[10] > 0.4:  # error rate
            risk += 0.3
        if features[6] < 0:  # negative trend
            risk += 0.2
        if features[15] > 0.5:  # fatigue
            risk += 0.2

        return min(1.0, risk)

    # -------------------------------
    # LEARNING SPEED
    # -------------------------------
    def learning_speed(self, features):
        trend = features[6]
        return "fast" if trend > 1 else "slow" if trend < 0 else "moderate"

    # -------------------------------
    # BURNOUT DETECTION
    # -------------------------------
    def detect_burnout(self, features):
        fatigue = features[15]
        trend = features[6]

        if fatigue > 0.5 and trend < 0:
            return True
        return False

    # -------------------------------
    # FINAL PREDICTION PACK
    # -------------------------------
    def predict(self, student_id, summary):

        self.update_history(student_id, summary)

        features = self.extract_features(student_id, summary)

        predicted_score = self.predict_score(features)
        risk = self.predict_failure_risk(features)
        speed = self.learning_speed(features)
        burnout = self.detect_burnout(features)

        return {
            "predicted_score": round(predicted_score, 2),
            "failure_risk": round(risk, 2),
            "learning_speed": speed,
            "burnout_risk": burnout
        }