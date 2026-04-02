# main.py - Advanced Adaptive Learning System with Teacher UI
import os
import logging
import secrets
from flask import Flask, jsonify, request, render_template_string, session, redirect
from flask_cors import CORS
import dotenv
from rich.console import Console

# Core imports
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

# Global system instance
system = None


class AdaptiveLearningSystem:
    def __init__(self):
        try:
            self.llm = LLMGroq(temperature=0.65)
            self.engine = AdaptiveEngine()

            self.prompt_engine = PromptEngine()
            self.response_optimizer = ResponseOptimizer()
            self.long_term_memory = LongTermMemory()
            self.decision_model = DecisionModel()
            self.reinforcement_model = ReinforcementModel()

            self.student_id = ""
            self.current_topic = "Cyber Security"
            self.total_questions = 10
            self.last_question = None

            logger.info("🚀 Advanced AdaptiveLearningSystem initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AdaptiveLearningSystem: {e}")
            raise


# Initialize system safely
try:
    system = AdaptiveLearningSystem()
except Exception as e:
    logger.critical(f"Critical failure during system init: {e}")
    system = None


# ====================== HOME PAGE - Student + Teacher Sections ======================
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
        </style>
    </head>
    <body class="bg-gradient-to-br from-indigo-950 via-purple-950 to-violet-950 text-white min-h-screen">
        <div class="max-w-5xl mx-auto pt-16 px-6">
            <div class="text-center mb-16">
                <h1 class="text-6xl md:text-7xl font-bold mb-4 bg-gradient-to-r from-indigo-300 to-violet-300 bg-clip-text text-transparent">
                    Adaptive Learning
                </h1>
                <p class="text-2xl md:text-3xl text-indigo-200">Personalized AI Quiz • For Students & Teachers</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-10">
                <!-- ==================== STUDENT SECTION ==================== -->
                <div class="glass rounded-3xl p-8 md:p-10 shadow-2xl border border-white/10">
                    <div class="text-center mb-8">
                        <div class="text-6xl mb-4">👨‍🎓</div>
                        <h2 class="text-4xl font-semibold">Student</h2>
                        <p class="text-indigo-200 mt-2">Take Adaptive Quiz</p>
                    </div>
                    
                    <form action="/start_quiz" method="POST" class="space-y-6">
                        <input type="text" name="student_name" placeholder="Enter your Name or ID" 
                               class="w-full p-5 rounded-2xl bg-white/10 text-white placeholder:text-white/70 focus:outline-none focus:ring-2 focus:ring-indigo-400 text-lg" required>
                        
                        <div>
                            <label class="block text-sm text-indigo-300 mb-2">Select Subject</label>
                            <select name="topic" class="w-full p-5 rounded-2xl text-base focus:outline-none focus:ring-2 focus:ring-indigo-400">
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
                                class="w-full bg-gradient-to-r from-indigo-500 via-violet-600 to-purple-600 hover:from-indigo-600 hover:via-violet-700 hover:to-purple-700 py-7 rounded-2xl font-semibold text-xl transition-all shadow-lg">
                            🚀 Start Adaptive Quiz
                        </button>
                    </form>
                </div>

                <!-- ==================== TEACHER SECTION ==================== -->
                <div class="glass rounded-3xl p-8 md:p-10 shadow-2xl border border-white/10">
                    <div class="text-center mb-8">
                        <div class="text-6xl mb-4">👨‍🏫</div>
                        <h2 class="text-4xl font-semibold">Teacher</h2>
                        <p class="text-indigo-200 mt-2">Create Quiz • Add Questions</p>
                    </div>
                    
                    <a href="/teacher_setup" 
                       class="block w-full text-center bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 py-7 rounded-2xl font-semibold text-xl transition-all shadow-lg">
                        👩‍🏫 Setup Quiz as Teacher
                    </a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)


# ====================== TEACHER SETUP ======================
@app.route("/teacher_setup")
def teacher_setup():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Teacher Setup</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>.glass { background: rgba(255,255,255,0.1); backdrop-filter: blur(20px); }</style>
    </head>
    <body class="bg-gradient-to-br from-indigo-950 via-purple-950 to-violet-950 text-white min-h-screen flex items-center justify-center">
        <div class="max-w-lg w-full mx-4 glass rounded-3xl p-12">
            <h1 class="text-4xl font-bold text-center mb-10">Teacher Quiz Setup</h1>
            
            <form action="/create_teacher_quiz" method="POST" class="space-y-8">
                <div>
                    <label class="block text-indigo-300 mb-2">Your Name</label>
                    <input type="text" name="teacher_name" placeholder="e.g. Mr. Sharma" required
                           class="w-full p-5 rounded-2xl bg-white/10 text-white text-lg focus:outline-none focus:ring-2 focus:ring-emerald-400">
                </div>
                <div>
                    <label class="block text-indigo-300 mb-2">Subject</label>
                    <input type="text" name="subject" value="Cyber Security" required
                           class="w-full p-5 rounded-2xl bg-white/10 text-white text-lg focus:outline-none focus:ring-2 focus:ring-emerald-400">
                </div>
                <div>
                    <label class="block text-indigo-300 mb-2">Number of Students</label>
                    <input type="number" name="num_students" value="25" min="1" max="100" required
                           class="w-full p-5 rounded-2xl bg-white/10 text-white text-lg focus:outline-none focus:ring-2 focus:ring-emerald-400">
                </div>
                
                <button type="submit" class="w-full bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 py-7 rounded-2xl font-bold text-2xl">
                    Create Quiz Room
                </button>
            </form>
        </div>
    </body>
    </html>
    """)


@app.route("/create_teacher_quiz", methods=["POST"])
def create_teacher_quiz():
    if not system:
        return "System not initialized", 500

    teacher_name = request.form.get("teacher_name", "Teacher").strip()
    subject = request.form.get("subject", "Cyber Security").strip()
    num_students = int(request.form.get("num_students", 25))

    room_code = secrets.token_hex(3).upper()

    session['teacher_name'] = teacher_name
    session['subject'] = subject
    session['room_code'] = room_code

    system.current_topic = subject

    return redirect(f"/teacher_control?room={room_code}")


# ====================== TEACHER CONTROL PANEL ======================
@app.route("/teacher_control")
def teacher_control():
    room_code = request.args.get("room") or session.get("room_code")
    if not room_code:
        return redirect("/")

    subject = session.get("subject", "Cyber Security")

    return render_template_string("""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>Teacher Control</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>.glass { background: rgba(255,255,255,0.1); backdrop-filter: blur(16px); }</style>
    </head>
    <body class="bg-gradient-to-br from-zinc-950 to-black text-white min-h-screen">
        <div class="max-w-6xl mx-auto p-8">
            <div class="flex justify-between items-center mb-10">
                <div>
                    <h1 class="text-4xl font-bold">Teacher Control Panel</h1>
                    <p class="text-emerald-400">Subject: {{ subject }} | Room Code: <span class="font-mono">{{ room_code }}</span></p>
                </div>
                <a href="/" class="px-6 py-3 bg-white/10 hover:bg-white/20 rounded-2xl">← Home</a>
            </div>

            <div class="grid lg:grid-cols-2 gap-10">
                <div class="glass rounded-3xl p-10">
                    <h2 class="text-3xl font-semibold mb-6">Add New Question</h2>
                    <input id="q" placeholder="Enter Question" class="w-full mb-4 p-5 rounded-2xl bg-zinc-900">
                    <div class="grid grid-cols-2 gap-4 mb-6">
                        <input id="opt1" placeholder="Option A" class="p-5 rounded-2xl bg-zinc-900">
                        <input id="opt2" placeholder="Option B" class="p-5 rounded-2xl bg-zinc-900">
                        <input id="opt3" placeholder="Option C" class="p-5 rounded-2xl bg-zinc-900">
                        <input id="opt4" placeholder="Option D" class="p-5 rounded-2xl bg-zinc-900">
                    </div>
                    <input id="correct" placeholder="Correct Option (A/B/C/D)" maxlength="1" 
                           class="w-full p-5 rounded-2xl bg-zinc-900 mb-8 text-center text-2xl">
                    <button onclick="addQuestion()" class="w-full bg-emerald-600 hover:bg-emerald-700 py-6 rounded-2xl font-bold text-xl">
                        Add Question
                    </button>
                </div>

                <div class="glass rounded-3xl p-10">
                    <h2 class="text-3xl font-semibold mb-6">Added Questions</h2>
                    <div id="list" class="space-y-4 min-h-[300px]"></div>
                    <button onclick="startQuiz()" class="mt-10 w-full bg-violet-600 hover:bg-violet-700 py-7 rounded-2xl font-bold text-2xl">
                        Start Quiz for Students
                    </button>
                </div>
            </div>
        </div>

        <script>
        let questions = [];
        function addQuestion() {
            const q = document.getElementById('q').value.trim();
            const correct = document.getElementById('correct').value.trim().toUpperCase();
            if (!q || !correct) return alert("Question and correct answer required");

            const options = [
                document.getElementById('opt1').value.trim(),
                document.getElementById('opt2').value.trim(),
                document.getElementById('opt3').value.trim(),
                document.getElementById('opt4').value.trim()
            ].filter(o => o);

            fetch('/add_teacher_question', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question: q, answer: correct, topic: "{{ subject }}", options: options})
            });

            questions.push({q, correct});
            renderList();
            document.getElementById('q').value = '';
            document.getElementById('correct').value = '';
        }

        function renderList() {
            document.getElementById('list').innerHTML = questions.map((item, i) => 
                `<div class="bg-zinc-900 p-5 rounded-2xl flex justify-between">
                    <span>Q${i+1}. ${item.q.substring(0,80)}...</span>
                    <span class="text-amber-400">(${item.correct})</span>
                </div>`
            ).join('');
        }

        function startQuiz() {
            alert("Quiz Started! Room Code: {{ room_code }}");
            window.location.href = "/quiz";
        }
        </script>
    </body></html>
    """, subject=subject, room_code=room_code)


# ====================== EXISTING QUIZ ROUTES (Unchanged) ======================
@app.route("/start_quiz", methods=["POST"])
def start_quiz():
    if not system: return "System not initialized", 500

    student_name = request.form.get("student_name", "Guest").strip()
    topic = request.form.get("topic", "Cyber Security").strip()

    session['student_id'] = student_name
    session['current_topic'] = topic
    system.student_id = student_name
    system.current_topic = topic

    try:
        system.engine.start_session(student_id=student_name, topic=topic)
        system.long_term_memory.get_student_knowledge(student_name)
    except Exception as e:
        logger.error(f"start_quiz error: {e}")

    return redirect("/quiz")


@app.route("/quiz")
def quiz_page():
    # Your original quiz page code (kept as is)
    return render_template_string(""" 
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>Adaptive Quiz</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>.glass { background: rgba(255,255,255,0.1); backdrop-filter: blur(16px); }</style>
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
            <button onclick="submitAnswer()" class="w-full bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 py-6 rounded-2xl font-semibold text-xl transition-all">Submit Answer</button>
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
            } catch (e) { console.error(e); }
        }

        async function submitAnswer() {
            if (!selectedAnswer) return alert("Please select an option");
            const res = await fetch('/answer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({answer: selectedAnswer})
            });
            const result = await res.json();
            const feedback = document.getElementById('feedback');
            feedback.innerHTML = result.correct 
                ? `<span class="text-emerald-400">✅ ${result.message || 'Excellent!'}</span>`
                : `<span class="text-red-400">❌ ${result.message || 'Incorrect'}</span>`;
            setTimeout(() => { selectedAnswer = ''; loadQuestion(); }, 1700);
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
        if "10 questions" in str(e).lower() or "limit" in str(e).lower():
            return jsonify({"redirect": "/results"}), 200
        logger.error(f"Question error: {e}")
        return jsonify({"error": "Failed to generate question"}), 500


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
        logger.error(f"Answer error: {e}")
        return jsonify({"correct": False, "message": "Error processing answer"}), 500


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
    <html><head><meta charset="UTF-8"><title>Results</title>
    <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gradient-to-br from-indigo-950 to-purple-950 text-white min-h-screen flex items-center justify-center">
        <div class="max-w-3xl w-full mx-4 glass rounded-3xl p-12">
            <h1 class="text-5xl font-bold mb-8 text-center">Quiz Completed!</h1>
            <div class="text-center mb-12">
                <div class="text-7xl font-bold mb-4">{{ correct }}/10</div>
                <div class="text-4xl text-emerald-400">Accuracy: {{ accuracy }}%</div>
                <div class="text-3xl mt-6">Final Score: <strong class="text-yellow-300">{{ final_score }}</strong></div>
            </div>
            <a href="/" class="block text-center py-5 bg-indigo-600 rounded-2xl font-semibold text-xl">Take Another Quiz</a>
        </div>
    </body></html>
    """, correct=correct, accuracy=accuracy, final_score=final_score, topic=topic)


# ====================== ADD TEACHER QUESTION ======================
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
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Teacher question error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ====================== ENTRY POINT ======================
if __name__ == "__main__":
    print("="*75)
    print("🌟 ADVANCED ADAPTIVE LEARNING SYSTEM STARTED")
    print("="*75)
    print("🔗 Main Portal : http://localhost:5000")
    print("👨‍🏫 Teacher Setup : http://localhost:5000/teacher_setup")
    print("="*75)
    app.run(host='0.0.0.0', port=5000, debug=True)