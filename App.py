from flask import Flask, jsonify

app = Flask(__name__)

# ================= ENGINE =================
class AdaptiveLearningSystem:
    def __init__(self):
        self.questions = [
            {"q": "2 + 2", "a": "4"},
            {"q": "5 + 3", "a": "8"}
        ]
        self.index = 0

    def get_question(self):
        q = self.questions[self.index]
        self.index = (self.index + 1) % len(self.questions)
        return q

engine = AdaptiveLearningSystem()

# ================= ROUTES =================
@app.route("/")
def home():
    return "Adaptive Learning System is Live 🚀"

@app.route("/question")
def question():
    q = engine.get_question()
    return jsonify(q)

# ================= RUN =================
if __name__ == "__main__":
    app.run(port=5000)