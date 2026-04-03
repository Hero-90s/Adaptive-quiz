# main.py - Advanced Adaptive Learning System (Final Fixed Version)
import os
import sys
import logging
from flask import Flask, jsonify, request, render_template_string, session, redirect
from flask_cors import CORS
import dotenv
from rich.console import Console
from Core.AI.llm_groq import LLMGroq
from Core.Engine.adaptive_engine import AdaptiveEngine
from Core.AI.prompt_engineering import PromptEngine
from Core.AI.response_optimizer import ResponseOptimizer
from Core.Memory.long_term_memory import LongTermMemory
from Core.Engine.decision_model import DecisionModel   
from Core.Engine.reinforcement_learning import ReinforcementModel
dotenv.load_dotenv()
console = Console()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.secret_key = "adaptive-secret-key-2026"

# Add current directory to Python path so Core folder can be found on Render
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Global system instance
system = None


class AdaptiveLearningSystem:
    def __init__(self):
        try:
            self.llm = LLMGroq(temperature=0.65)
            self.engine = AdaptiveEngine()

            # Full integration of all modules
            self.prompt_engine = PromptEngine()
            self.response_optimizer = ResponseOptimizer()
            self.long_term_memory = LongTermMemory()
            self.decision_model = DecisionModel()
            self.reinforcement_model = ReinforcementModel()

            self.student_id = ""
            self.current_topic = "Cyber Security"
            self.total_questions = 10
            self.last_question = None

            logger.info("🚀 Advanced AdaptiveLearningSystem initialized successfully with all modules")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AdaptiveLearningSystem: {e}")
            raise


# Initialize system safely
try:
    system = AdaptiveLearningSystem()
except Exception as e:
    logger.critical(f"Critical failure during system init: {e}")
    system = None


# ====================== HOME PAGE (Improved Dropdown Visibility) ======================
@app.route("/")
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Adaptive Learning</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { font-family: 'Inter', system-ui; }
            .glass { 
                background: rgba(255,255,255,0.12); 
                backdrop-filter: blur(20px); 
            }
            select {
                color: white;
                background-color: rgba(255,255,255,0.15);
                border: 1px solid rgba(255,255,255,0.3);
            }
            select option {
                color: #1f2937;
                background-color: white;
                padding: 12px 16px;
            }
            select:focus {
                background-color: rgba(255,255,255,0.25);
                border-color: rgb(129 140 248);
                box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.3);
            }
        </style>
    </head>
    <body class="bg-gradient-to-br from-indigo-950 via-purple-950 to-violet-950 text-white min-h-screen">
        <div class="max-w-md mx-auto pt-28 px-6">
            <div class="text-center mb-12">
                <h1 class="text-6xl font-bold mb-4 bg-gradient-to-r from-indigo-300 to-violet-300 bg-clip-text text-transparent">
                    Adaptive Learning
                </h1>
                <p class="text-2xl text-indigo-200">Personalized AI Tutor • 10 Adaptive Questions</p>
            </div>
            
            <div class="glass rounded-3xl p-10 shadow-2xl border border-white/10">
                <form action="/start_quiz" method="POST" class="space-y-6">
                    <div>
                        <input type="text" name="student_name" placeholder="Enter your Name or ID" 
                               class="w-full p-4 rounded-2xl bg-white/10 text-white placeholder:text-white/70 focus:outline-none focus:ring-2 focus:ring-indigo-400 text-lg" required>
                    </div>
                    
                    <div>
                        <label class="block text-sm text-indigo-300 mb-2">Select Subject</label>
                        <select name="topic" 
                                class="w-full p-4 rounded-2xl text-base focus:outline-none focus:ring-2 focus:ring-indigo-400">
                            <option value="Cyber Security">🔒 Cyber Security</option>
                            <option value="Python Programming">🐍 Python Programming</option>
                            <option value="Data Structures">📚 Data Structures</option>
                            <option value="Operating Systems">💻 Operating Systems</option>
                            <option value="DBMS">🗄️ Database Management System</option>
                            <option value="Networking">🌐 Computer Networking</option>
                            <option value="Artificial Intelligence">🤖 Artificial Intelligence</option>
                        </select>
                    </div>

                    <button type="submit" 
                            class="w-full bg-gradient-to-r from-indigo-500 via-violet-600 to-purple-600 hover:from-indigo-600 hover:via-violet-700 hover:to-purple-700 py-6 rounded-2xl font-semibold text-xl transition-all duration-300 shadow-lg">
                        🚀 Start Adaptive Test
                    </button>
                </form>
            </div>
            
            <p class="text-center text-white/60 mt-8 text-sm">10 questions • Adaptive difficulty • Real-time feedback</p>
        </div>
    </body>
    </html>
    """)


@app.route("/start_quiz", methods=["POST"])
def start_quiz():
    if not system:
        return "System not initialized. Please check logs.", 500

    student_name = request.form.get("student_name", "Guest").strip()
    topic = request.form.get("topic", "Cyber Security").strip()

    if not student_name:
        student_name = "Guest"

    session['student_id'] = student_name
    session['current_topic'] = topic

    system.student_id = student_name
    system.current_topic = topic

    try:
        system.engine.start_session(student_id=student_name, topic=topic)
        system.long_term_memory.get_student_knowledge(student_name)
        logger.info(f"New quiz started by {student_name} on {topic}")
    except Exception as e:
        logger.error(f"start_quiz error: {e}")

    return redirect("/quiz")


# ====================== QUIZ PAGE ======================
@app.route("/quiz")
def quiz_page():
    return render_template_string("""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>Adaptive Quiz</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .glass { background: rgba(255,255,255,0.1); backdrop-filter: blur(16px); }
    </style>
    </head>
    <body class="bg-gradient-to-br from-indigo-950 to-purple-950 text-white min-h-screen flex items-center justify-center">
        <div class="max-w-2xl w-full mx-4 glass rounded-3xl p-10 shadow-2xl">
            <div class="flex justify-between items-center mb-8">
                <div>
                    <span class="text-indigo-300">Question</span>
                    <span id="progress" class="text-3xl font-bold text-white"><span id="current-q">1</span>/10</span>
                </div>
                <div id="difficulty" class="px-5 py-2 bg-white/10 rounded-2xl text-sm font-medium"></div>
            </div>
            
            <h2 id="question-text" class="text-3xl font-medium mb-10 min-h-[120px] leading-tight"></h2>
            
            <div id="options" class="space-y-4 mb-10"></div>
            
            <button onclick="submitAnswer()" 
                    class="w-full bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 py-6 rounded-2xl font-semibold text-xl transition-all">
                Submit Answer
            </button>
            
            <div id="feedback" class="mt-10 text-center text-xl min-h-[80px]"></div>
        </div>

        <script>
        let selectedAnswer = '';
        let isQuizOver = false;

        async function loadQuestion() {
            if (isQuizOver) return;

            try {
                const res = await fetch('/question');
                const data = await res.json();

                if (data.redirect === "/results") {
                    isQuizOver = true;
                    window.location.href = "/results";
                    return;
                }

                if (data.error) {
                    document.getElementById('question-text').innerHTML = `<span class="text-red-400">⚠️ ${data.error}</span>`;
                    return;
                }

                document.getElementById('current-q').textContent = data.questions_asked || 1;
                document.getElementById('difficulty').innerHTML = `Difficulty: <span class="text-emerald-400">${data.difficulty || 2.5}</span>`;

                document.getElementById('question-text').innerHTML = data.question;

                const optionsDiv = document.getElementById('options');
                optionsDiv.innerHTML = '';

                if (data.options && data.options.length > 0) {
                    data.options.forEach((opt, index) => {
                        const letter = String.fromCharCode(65 + index);
                        const div = document.createElement('div');
                        div.className = 'p-6 bg-white/10 hover:bg-white/20 rounded-2xl cursor-pointer transition-all flex items-center gap-4 text-white text-lg';
                        div.innerHTML = `<span class="font-bold text-2xl w-10 text-indigo-300">${letter}.</span> ${opt}`;
                        div.onclick = () => {
                            selectedAnswer = letter;
                            document.querySelectorAll('#options > div').forEach(d => d.classList.remove('ring-2', 'ring-indigo-400'));
                            div.classList.add('ring-2', 'ring-indigo-400');
                        };
                        optionsDiv.appendChild(div);
                    });
                }
            } catch (e) {
                console.error("Load question error:", e);
            }
        }

        async function submitAnswer() {
            if (!selectedAnswer) {
                alert("⚠️ Please select an option");
                return;
            }
            
            const res = await fetch('/answer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({answer: selectedAnswer})
            });
            
            const result = await res.json();
            
            const feedback = document.getElementById('feedback');
            if (result.correct) {
                feedback.innerHTML = `<span class="text-emerald-400">✅ ${result.message || 'Excellent!'}</span>`;
            } else {
                feedback.innerHTML = `<span class="text-red-400">❌ ${result.message || 'Incorrect'}</span>`;
            }

            setTimeout(() => { 
                selectedAnswer = ''; 
                loadQuestion(); 
            }, 1700);
        }

        window.onload = loadQuestion;
        </script>
    </body></html>
    """)


@app.route("/question")
def get_question():
    if not system:
        return jsonify({"error": "System not initialized"}), 500

    try:
        q = system.engine.get_question(system.student_id)
        system.last_question = q

        session_data = system.engine.current_session.get(system.student_id, {})

        return jsonify({
            "question": q.question,
            "topic": q.topic,
            "difficulty": getattr(q, 'difficulty', 2.5),
            "options": q.options or [],
            "questions_asked": session_data.get("questions_asked", 1)
        })
    except Exception as e:
        error_str = str(e).lower()
        if "10 questions" in error_str or "limit reached" in error_str:
            return jsonify({"redirect": "/results"}), 200

        logger.error(f"Question generation error: {e}")
        return jsonify({"error": "Failed to generate question. Please try again."}), 500


@app.route("/answer", methods=["POST"])
def answer():
    if not system or not system.last_question:
        return jsonify({"correct": False, "message": "No active question"}), 400

    try:
        data = request.json
        user_answer = data.get("answer", "").strip().upper()

        result = system.engine.submit_answer(
            student_id=system.student_id,
            question=system.last_question,
            user_answer=user_answer,
            response_time=15,
            confidence=0.7
        )
        return jsonify(result)
    except Exception as e:
        logger.error(f"Answer submission error: {e}")
        return jsonify({"correct": False, "message": "Error processing your answer"}), 500


# ====================== RESULTS PAGE ======================
@app.route("/results")
def results():
    if not system or system.student_id not in system.engine.current_session:
        return redirect("/")

    session_data = system.engine.current_session[system.student_id]
    correct = session_data.get("correct_answers", 0)
    accuracy = round((correct / 10) * 100, 1)
    final_score = session_data.get("score", 0)
    topic = session_data.get("topic", "Cyber Security")

    system.engine.update_leaderboard(system.student_id, final_score, accuracy, topic)
    leaderboard = system.engine.get_leaderboard(limit=10)

    ranked_leaderboard = [
        {"rank": i+1, "student_id": p.get("student_id", "Unknown"), 
         "score": p.get("score", 0), "accuracy": p.get("accuracy", 0)}
        for i, p in enumerate(leaderboard)
    ]

    return render_template_string("""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>Quiz Results</title>
    <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gradient-to-br from-indigo-950 to-purple-950 text-white min-h-screen flex items-center justify-center">
        <div class="max-w-3xl w-full mx-4 glass rounded-3xl p-12 shadow-2xl">
            <h1 class="text-5xl font-bold mb-8 text-center">🎉 Quiz Completed Successfully!</h1>
            
            <div class="text-center mb-12">
                <div class="text-7xl font-bold mb-4">{{ correct }}/10</div>
                <div class="text-4xl text-emerald-400">Accuracy: {{ accuracy }}%</div>
                <div class="text-3xl mt-6">Final Score: <strong class="text-yellow-300">{{ final_score }}</strong></div>
                <p class="mt-4 text-indigo-200">Topic: <strong>{{ topic }}</strong></p>
            </div>

            <h2 class="text-2xl font-semibold mb-6 text-center">🏆 Global Leaderboard</h2>
            <div class="bg-white/10 rounded-2xl p-6 max-h-96 overflow-auto">
                {% for player in ranked_leaderboard %}
                <div class="flex justify-between items-center py-4 border-b border-white/20 last:border-none">
                    <div class="flex items-center gap-4">
                        <span class="text-3xl font-bold text-yellow-400">#{{ player.rank }}</span>
                        <span class="text-xl">{{ player.student_id }}</span>
                    </div>
                    <div class="text-right">
                        <span class="font-semibold text-lg">{{ player.score }} pts</span><br>
                        <span class="text-emerald-400">{{ player.accuracy }}%</span>
                    </div>
                </div>
                {% else %}
                <p class="text-center py-12 text-gray-400">No scores recorded yet. Complete a quiz to appear here!</p>
                {% endfor %}
            </div>

            <div class="mt-12 flex gap-4 justify-center">
                <a href="/" class="px-10 py-5 bg-gradient-to-r from-indigo-500 to-violet-600 rounded-2xl font-semibold text-xl hover:scale-105 transition-all">
                    Take Another Quiz
                </a>
            </div>
        </div>
    </body></html>
    """, correct=correct, accuracy=accuracy, final_score=final_score, topic=topic, ranked_leaderboard=ranked_leaderboard)


# ====================== TEACHER DASHBOARD ======================
@app.route("/teacher")
def teacher_dashboard():
    return render_template_string("""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>Teacher Dashboard - Adaptive Learning</title>
    <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-zinc-950 text-white p-8">
        <div class="max-w-4xl mx-auto">
            <h1 class="text-5xl font-bold mb-10 text-center">👨‍🏫 Teacher Dashboard</h1>
            <div class="bg-zinc-900 rounded-3xl p-10">
                <h2 class="text-3xl mb-8">Add New MCQ Question</h2>
                <input id="q" placeholder="Enter Question" class="w-full mb-5 p-5 rounded-2xl bg-zinc-800 text-white text-lg">
                <input id="a" placeholder="Correct Option Letter (A/B/C/D)" class="w-full mb-5 p-5 rounded-2xl bg-zinc-800 text-white text-lg">
                <div class="grid grid-cols-2 gap-4 mb-8">
                    <input id="opt1" placeholder="Option A" class="p-5 rounded-2xl bg-zinc-800 text-white">
                    <input id="opt2" placeholder="Option B" class="p-5 rounded-2xl bg-zinc-800 text-white">
                    <input id="opt3" placeholder="Option C" class="p-5 rounded-2xl bg-zinc-800 text-white">
                    <input id="opt4" placeholder="Option D" class="p-5 rounded-2xl bg-zinc-800 text-white">
                </div>
                <input id="topic" value="Cyber Security" class="w-full mb-8 p-5 rounded-2xl bg-zinc-800 text-white">
                
                <button onclick="addQuestion()" 
                        class="w-full bg-emerald-600 hover:bg-emerald-700 py-6 rounded-2xl font-bold text-xl transition-all">
                    ➕ Add Question to Database
                </button>
            </div>
        </div>
        <script>
        async function addQuestion() {
            const q = document.getElementById('q').value.trim();
            const a = document.getElementById('a').value.trim().toUpperCase();
            const topic = document.getElementById('topic').value.trim();
            const options = [
                document.getElementById('opt1').value.trim(),
                document.getElementById('opt2').value.trim(),
                document.getElementById('opt3').value.trim(),
                document.getElementById('opt4').value.trim()
            ];

            if (!q || !a) {
                alert("❌ Question and correct option are required");
                return;
            }

            await fetch('/add_teacher_question', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question: q, answer: a, topic: topic, options: options})
            });
            
            alert("✅ Question added successfully!");
            // Clear inputs
            ['q','a','opt1','opt2','opt3','opt4'].forEach(id => document.getElementById(id).value = '');
        }
        </script>
    </body></html>
    """)


@app.route("/add_teacher_question", methods=["POST"])
def add_teacher_question():
    try:
        data = request.json
        system.engine.add_teacher_question(
            data["question"], 
            data["answer"], 
            data.get("topic", "Cyber Security"),
            data.get("options")
        )
        return jsonify({"status": "success", "message": "Question added successfully"})
    except Exception as e:
        logger.error(f"Teacher question error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ====================== ENTRY POINT ======================
if __name__ == "__main__":
    print("="*60)
    print("🌟 ADVANCED ADAPTIVE LEARNING SYSTEM STARTED")
    print("="*60)
    print("🔗 Student Portal : http://localhost:5000")
    print("👨‍🏫 Teacher Dashboard : http://localhost:5000/teacher")
    print("📌 Run with ngrok: ngrok http 5000")
    print("="*60)
    app.run(host='0.0.0.0', port=5000, debug=True)
