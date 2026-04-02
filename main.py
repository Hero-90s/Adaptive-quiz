# main.py - MAXED LEVEL Adaptive Learning System with Teacher UI
import os
import logging
import secrets
from flask import Flask, jsonify, request, render_template_string, session, redirect
from flask_cors import CORS
import dotenv

dotenv.load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.secret_key = "adaptive-secret-key-2026"

# ====================== Try to load Core System (with fallback) ======================
system = None
try:
    from Core.AI.llm_groq import LLMGroq
    from Core.Engine.adaptive_engine import AdaptiveEngine
    from Core.AI.prompt_engineering import PromptEngine
    from Core.AI.response_optimizer import ResponseOptimizer
    from Core.Memory.long_term_memory import LongTermMemory
    from Core.Engine.decision_model import DecisionModel
    from Core.Engine.reinforcement_learning import ReinforcementModel

    class AdaptiveLearningSystem:
        def __init__(self):
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
            logger.info("🚀 Full AdaptiveLearningSystem loaded successfully")

    system = AdaptiveLearningSystem()
    logger.info("✅ Core system initialized")
except Exception as e:
    logger.warning(f"⚠️ Core modules failed to load: {e}. Running in limited mode.")
    system = None


# ====================== HOME PAGE - Student + Teacher ======================
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
            .glass { background: rgba(255,255,255,0.12); backdrop-filter: blur(20px); }
        </style>
    </head>
    <body class="bg-gradient-to-br from-indigo-950 via-purple-950 to-violet-950 text-white min-h-screen">
        <div class="max-w-5xl mx-auto pt-12 px-6">
            <div class="text-center mb-16">
                <h1 class="text-6xl md:text-7xl font-bold mb-4 bg-gradient-to-r from-indigo-300 to-violet-300 bg-clip-text text-transparent">
                    Adaptive Learning
                </h1>
                <p class="text-2xl md:text-3xl text-indigo-200">AI-Powered Quiz System</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-10">
                <!-- Student Card -->
                <div class="glass rounded-3xl p-8 md:p-10 shadow-2xl">
                    <div class="text-center mb-8">
                        <div class="text-6xl mb-4">👨‍🎓</div>
                        <h2 class="text-4xl font-semibold">Student</h2>
                        <p class="text-indigo-200 mt-2">Take Personalized Adaptive Quiz</p>
                    </div>
                    <form action="/start_quiz" method="POST" class="space-y-6">
                        <input type="text" name="student_name" placeholder="Enter your Name" required
                               class="w-full p-5 rounded-2xl bg-white/10 text-white text-lg focus:outline-none focus:ring-2 focus:ring-indigo-400">
                        <select name="topic" class="w-full p-5 rounded-2xl bg-white/10 text-lg focus:outline-none focus:ring-2 focus:ring-indigo-400">
                            <option value="Cyber Security">🔒 Cyber Security</option>
                            <option value="Python Programming">🐍 Python Programming</option>
                            <option value="Data Structures">📚 Data Structures</option>
                            <option value="Operating Systems">💻 Operating Systems</option>
                            <option value="DBMS">🗄️ DBMS</option>
                            <option value="Networking">🌐 Networking</option>
                            <option value="Artificial Intelligence">🤖 Artificial Intelligence</option>
                        </select>
                        <button type="submit" 
                                class="w-full py-7 rounded-2xl font-semibold text-xl bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 transition-all">
                            🚀 Start Adaptive Quiz
                        </button>
                    </form>
                </div>

                <!-- Teacher Card -->
                <div class="glass rounded-3xl p-8 md:p-10 shadow-2xl">
                    <div class="text-center mb-8">
                        <div class="text-6xl mb-4">👨‍🏫</div>
                        <h2 class="text-4xl font-semibold">Teacher</h2>
                        <p class="text-indigo-200 mt-2">Create Quiz • Add Custom Questions</p>
                    </div>
                    <a href="/teacher_setup" 
                       class="block w-full py-7 rounded-2xl font-semibold text-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 transition-all text-center">
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
    <body class="bg-gradient-to-br from-indigo-950 to-violet-950 text-white min-h-screen flex items-center justify-center">
        <div class="max-w-lg w-full mx-4 glass rounded-3xl p-12">
            <h1 class="text-4xl font-bold text-center mb-10">Teacher Quiz Setup</h1>
            <form action="/create_teacher_quiz" method="POST" class="space-y-8">
                <div>
                    <label class="block text-indigo-300 mb-2">Teacher Name</label>
                    <input type="text" name="teacher_name" placeholder="e.g. Mr. Sharma" required class="w-full p-5 rounded-2xl bg-white/10 text-white text-lg">
                </div>
                <div>
                    <label class="block text-indigo-300 mb-2">Subject</label>
                    <input type="text" name="subject" value="Cyber Security" required class="w-full p-5 rounded-2xl bg-white/10 text-white text-lg">
                </div>
                <div>
                    <label class="block text-indigo-300 mb-2">Number of Students</label>
                    <input type="number" name="num_students" value="25" min="1" max="100" required class="w-full p-5 rounded-2xl bg-white/10 text-white text-lg">
                </div>
                <button type="submit" class="w-full py-7 rounded-2xl font-bold text-2xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700">
                    Create Quiz Room
                </button>
            </form>
        </div>
    </body>
    </html>
    """)


@app.route("/create_teacher_quiz", methods=["POST"])
def create_teacher_quiz():
    teacher_name = request.form.get("teacher_name", "Teacher").strip()
    subject = request.form.get("subject", "Cyber Security").strip()
    num_students = int(request.form.get("num_students", 25))

    room_code = secrets.token_hex(3).upper()

    session['teacher_name'] = teacher_name
    session['subject'] = subject
    session['room_code'] = room_code

    return redirect(f"/teacher_control?room={room_code}")


# ====================== TEACHER CONTROL PANEL (Maxed UI) ======================
@app.route("/teacher_control")
def teacher_control():
    room_code = request.args.get("room") or session.get("room_code", "XXXXXX")
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
                    <h1 class="text-5xl font-bold">👨‍🏫 Teacher Control Panel</h1>
                    <p class="text-xl text-emerald-400 mt-2">Subject: <strong>{{ subject }}</strong> | Room Code: <span class="font-mono bg-white/10 px-4 py-2 rounded-xl">{{ room_code }}</span></p>
                </div>
                <a href="/" class="px-8 py-4 bg-white/10 hover:bg-white/20 rounded-2xl">← Home</a>
            </div>

            <div class="grid lg:grid-cols-2 gap-10">
                <!-- Add Question -->
                <div class="glass rounded-3xl p-10">
                    <h2 class="text-3xl font-semibold mb-8">➕ Add New MCQ Question</h2>
                    <input id="q" placeholder="Enter full question" class="w-full p-5 rounded-2xl bg-zinc-900 text-white mb-6">
                    <div class="grid grid-cols-2 gap-4 mb-8">
                        <input id="opt1" placeholder="Option A" class="p-5 rounded-2xl bg-zinc-900">
                        <input id="opt2" placeholder="Option B" class="p-5 rounded-2xl bg-zinc-900">
                        <input id="opt3" placeholder="Option C" class="p-5 rounded-2xl bg-zinc-900">
                        <input id="opt4" placeholder="Option D" class="p-5 rounded-2xl bg-zinc-900">
                    </div>
                    <input id="correct" placeholder="Correct Answer (A/B/C/D)" maxlength="1" 
                           class="w-full p-5 rounded-2xl bg-zinc-900 text-center text-2xl font-bold mb-8">
                    <button onclick="addQuestion()" class="w-full py-6 bg-emerald-600 hover:bg-emerald-700 rounded-2xl font-bold text-xl">
                        Add Question to Quiz
                    </button>
                </div>

                <!-- Questions List + Start -->
                <div class="glass rounded-3xl p-10">
                    <h2 class="text-3xl font-semibold mb-6">📋 Added Questions</h2>
                    <div id="list" class="space-y-4 max-h-[420px] overflow-auto mb-10"></div>
                    <button onclick="startQuiz()" class="w-full py-7 bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 rounded-2xl font-bold text-2xl shadow-xl">
                        🚀 Start Quiz for Students
                    </button>
                    <p class="text-center text-white/60 mt-6">Share Room Code: <strong>{{ room_code }}</strong></p>
                </div>
            </div>
        </div>

        <script>
        let questions = [];
        function addQuestion() {
            const q = document.getElementById('q').value.trim();
            const correct = document.getElementById('correct').value.trim().toUpperCase();
            if (!q || !correct) return alert("Question and correct answer are required!");

            const options = [
                document.getElementById('opt1').value.trim(),
                document.getElementById('opt2').value.trim(),
                document.getElementById('opt3').value.trim(),
                document.getElementById('opt4').value.trim()
            ].filter(Boolean);

            fetch('/add_teacher_question', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question: q, answer: correct, topic: "{{ subject }}", options: options})
            }).then(() => {
                questions.push({q: q, correct: correct});
                renderList();
                // Clear inputs
                document.getElementById('q').value = '';
                document.getElementById('correct').value = '';
                ['opt1','opt2','opt3','opt4'].forEach(id => document.getElementById(id).value = '');
            });
        }

        function renderList() {
            document.getElementById('list').innerHTML = questions.map((item, i) => `
                <div class="bg-zinc-900 p-6 rounded-2xl flex justify-between items-center">
                    <div>Q${i+1}. ${item.q.substring(0, 85)}${item.q.length > 85 ? '...' : ''}</div>
                    <span class="px-4 py-1 bg-amber-500/20 text-amber-400 rounded-xl font-mono">(${item.correct})</span>
                </div>
            `).join('');
        }

        function startQuiz() {
            if (questions.length === 0) return alert("Add at least one question first!");
            alert(`Quiz Started Successfully!\\n\\nRoom Code: {{ room_code }}\\n\\nStudents can now join.`);
            window.location.href = "/quiz";
        }

        window.onload = renderList;
        </script>
    </body></html>
    """, subject=subject, room_code=room_code)


# ====================== STUDENT QUIZ ROUTES ======================
@app.route("/start_quiz", methods=["POST"])
def start_quiz():
    student_name = request.form.get("student_name", "Guest").strip()
    topic = request.form.get("topic", "Cyber Security").strip()

    session['student_id'] = student_name
    session['current_topic'] = topic

    if system:
        system.student_id = student_name
        system.current_topic = topic
        try:
            system.engine.start_session(student_id=student_name, topic=topic)
        except:
            pass

    return redirect("/quiz")


@app.route("/quiz")
def quiz_page():
    return render_template_string(""" 
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8"><title>Adaptive Quiz</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>.glass { background: rgba(255,255,255,0.1); backdrop-filter: blur(16px); }</style>
    </head>
    <body class="bg-gradient-to-br from-indigo-950 to-purple-950 text-white min-h-screen flex items-center justify-center">
        <div class="max-w-2xl w-full mx-4 glass rounded-3xl p-10 shadow-2xl">
            <div class="flex justify-between items-center mb-8">
                <div><span class="text-indigo-300">Question</span> <span id="progress" class="text-3xl font-bold"><span id="current-q">1</span>/10</span></div>
                <div id="difficulty" class="px-5 py-2 bg-white/10 rounded-2xl text-sm"></div>
            </div>
            <h2 id="question-text" class="text-3xl font-medium mb-10 min-h-[120px]"></h2>
            <div id="options" class="space-y-4 mb-10"></div>
            <button onclick="submitAnswer()" class="w-full py-6 bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 rounded-2xl font-semibold text-xl">Submit Answer</button>
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
                document.getElementById('difficulty').innerHTML = `Difficulty: <span class="text-emerald-400">${data.difficulty || 'Medium'}</span>`;
                document.getElementById('question-text').innerHTML = data.question;

                const div = document.getElementById('options');
                div.innerHTML = '';
                (data.options || []).forEach((opt, i) => {
                    const letter = String.fromCharCode(65 + i);
                    const el = document.createElement('div');
                    el.className = 'p-6 bg-white/10 hover:bg-white/20 rounded-2xl cursor-pointer transition-all flex items-center gap-4 text-lg';
                    el.innerHTML = `<span class="font-bold text-2xl w-10 text-indigo-300">${letter}.</span> ${opt}`;
                    el.onclick = () => {
                        selectedAnswer = letter;
                        document.querySelectorAll('#options > div').forEach(d => d.classList.remove('ring-2', 'ring-indigo-400'));
                        el.classList.add('ring-2', 'ring-indigo-400');
                    };
                    div.appendChild(el);
                });
            } catch(e) { console.error(e); }
        }

        async function submitAnswer() {
            if (!selectedAnswer) return alert("Please select an option");
            const res = await fetch('/answer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({answer: selectedAnswer})
            });
            const result = await res.json();
            document.getElementById('feedback').innerHTML = result.correct 
                ? `<span class="text-emerald-400">✅ ${result.message || 'Correct!'}</span>`
                : `<span class="text-red-400">❌ ${result.message || 'Incorrect'}</span>`;
            setTimeout(() => { selectedAnswer = ''; loadQuestion(); }, 1600);
        }

        window.onload = loadQuestion;
        </script>
    </body></html>
    """)


@app.route("/question")
def get_question():
    if not system:
        return jsonify({"error": "System not ready"}), 500
    try:
        q = system.engine.get_question(system.student_id)
        system.last_question = q
        session_data = system.engine.current_session.get(system.student_id, {})
        return jsonify({
            "question": q.question,
            "options": q.options or [],
            "difficulty": getattr(q, 'difficulty', 2.5),
            "questions_asked": session_data.get("questions_asked", 1)
        })
    except Exception as e:
        if "10 questions" in str(e).lower():
            return jsonify({"redirect": "/results"}), 200
        return jsonify({"error": "Failed to load question"}), 500


@app.route("/answer", methods=["POST"])
def answer():
    if not system or not system.last_question:
        return jsonify({"correct": False, "message": "No question active"}), 400
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
    return render_template_string("""
    <h1 class="text-5xl text-center mt-20">🎉 Quiz Completed!</h1>
    <p class="text-center mt-10"><a href="/" class="text-indigo-400 underline">Take Another Quiz</a></p>
    """)


# ====================== TEACHER QUESTION ADD ======================
@app.route("/add_teacher_question", methods=["POST"])
def add_teacher_question():
    try:
        data = request.json
        if system and hasattr(system.engine, 'add_teacher_question'):
            system.engine.add_teacher_question(
                data["question"], 
                data["answer"], 
                data.get("topic", "Cyber Security"),
                data.get("options")
            )
        return jsonify({"status": "success", "message": "Question added"})
    except Exception as e:
        logger.error(f"Add question error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ====================== ENTRY POINT ======================
if __name__ == "__main__":
    print("="*80)
    print("🌟 MAXED ADAPTIVE LEARNING SYSTEM STARTED")
    print("="*80)
    print("🔗 Live URL : http://localhost:5000")
    print("="*80)
    app.run(host='0.0.0.0', port=5000, debug=False)
