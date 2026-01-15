from flask import Flask, render_template_string, request, redirect, url_for
from datetime import datetime
import json
import os

app = Flask(__name__)
TASKS_FILE = "tasks.json"

if os.path.exists(TASKS_FILE):
    with open(TASKS_FILE, "r") as f:
        tasks = json.load(f)
else:
    tasks = []

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AcademAssist</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f0f4f8; }
        h1 { color: #1d3557; text-align: center; }
        section { background: white; padding: 25px; margin-bottom: 30px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);}
        input, textarea, select { width: 100%; padding: 8px; margin-top: 5px; margin-bottom: 15px; border-radius: 5px; border: 1px solid #ccc; }
        button { padding: 8px 15px; margin-top: 10px; background: #457b9d; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #1d3557; }
        ul { padding-left: 20px; }
        li { margin-bottom: 12px; padding: 8px; border-radius: 8px; }
        a { color: #1d3557; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .warning { color: red; font-weight: bold; }
        .complete-btn { background: #2a9d8f; margin-left: 10px; }
        .complete-btn:hover { background: #21867a; }
        .tips { font-style: italic; color: #555; margin-top: 5px; }
        .subject { display: inline-block; padding: 3px 8px; border-radius: 5px; color: white; font-weight: bold; margin-right: 5px; }
        .Science { background-color: #4caf50; }
        .Math { background-color: #2196f3; }
        .History { background-color: #ff9800; }
        .Default { background-color: #9e9e9e; }
        .High { background-color: #d32f2f; color: white; font-weight: bold; padding: 3px 7px; border-radius: 4px; margin-left: 5px; }
        .Medium { background-color: #fbc02d; color: white; font-weight: bold; padding: 3px 7px; border-radius: 4px; margin-left: 5px; }
        .Low { background-color: #388e3c; color: white; font-weight: bold; padding: 3px 7px; border-radius: 4px; margin-left: 5px; }
        .notes { margin-top: 5px; color: #333; font-size: 0.95em; }
        .dashboard { background-color: #e0f7fa; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
        .dashboard p { margin: 5px 0; font-weight: bold; }
        .subtopic { margin-left: 20px; }
        .flashcard { margin-top: 10px; background-color: #f1f1f1; padding: 8px; border-radius: 6px; }
        .answer { display: none; color: #d32f2f; margin-top: 5px; }
    </style>
    <script>
        function toggleAnswer(id) {
            const el = document.getElementById(id);
            if (el.style.display === "none") { el.style.display = "block"; }
            else { el.style.display = "none"; }
        }
    </script>
</head>
<body>

<h1>🎓 AcademAssist</h1>

<section class="dashboard">
<h2>📊 Progress Dashboard</h2>
<p>Total Assignments: {{ total_assignments }}</p>
<p>Completed Assignments: {{ completed_assignments }}</p>
<p>Assignments Due Soon (≤3 days): {{ due_soon_count }}</p>
</section>

<section>
<h2>📖 Create a Study Guide</h2>
<form method="post">
    <input type="hidden" name="form_type" value="study">
    Subject: <input type="text" name="subject" required><br>
    Topics (comma-separated):<br>
    <textarea name="topics" rows="3" required></textarea><br>
    <button type="submit">Generate Study Guide</button>
</form>

{% if guide %}
<h3>Study Guide</h3>
{% for topic, info in guide.items() %}
<h4>{{ topic }}</h4>
<ul>
{% for subtopic in info %}
<li class="subtopic">
<b>{{ subtopic['name'] }}</b><br>
{% for link in subtopic['links'] %}
<a href="{{ link }}" target="_blank">{{ link }}</a><br>
{% endfor %}
<div class="tips"><i>{{ subtopic['tip'] }}</i></div>
<div class="tips"><b>Summary Prompt:</b> Write 2-3 sentences summarizing this topic in your own words.</div>

{% if subtopic.get('quiz') %}
<div class="flashcard">
<b>Quiz Question:</b> {{ subtopic['quiz']['question'] }}<br>
{% set safe_id = topic|replace(' ', '')|replace('-', '')|replace('.', '') ~ loop.index0 %}
<button type="button" onclick="toggleAnswer('answer{{ safe_id }}')">Show/Hide Answer</button>
<div class="answer" id="answer{{ safe_id }}">{{ subtopic['quiz']['answer'] }}</div>
</div>
{% endif %}

</li>
{% endfor %}
</ul>
{% endfor %}
{% endif %}
</section>

<section>
<h2>📝 Assignment Tracker</h2>

{% if error_msg %}
<p class="warning">{{ error_msg }}</p>
{% endif %}

<form method="post">
    <input type="hidden" name="form_type" value="task">
    Assignment Name:
    <input type="text" name="task" required>
    Subject:
    <select name="subject_name">
        <option value="Default">Default</option>
        <option value="Science">Science</option>
        <option value="Math">Math</option>
        <option value="History">History</option>
    </select>
    Priority:
    <select name="priority">
        <option value="High">High</option>
        <option value="Medium">Medium</option>
        <option value="Low">Low</option>
    </select>
    Due Date:
    <input type="date" name="due" required>
    Notes (optional):
    <textarea name="notes" rows="2"></textarea>
    <button type="submit">Add Assignment</button>
</form>

<ul>
{% for t in tasks %}
<li>
<span class="subject {{ t.subject_name }}">{{ t.subject_name }}</span>
<b>{{ t.task }}</b>
<span class="{{ t.priority }}">{{ t.priority }}</span> – Due {{ t.due }}
{% if t.due_soon %}
<span class="warning">⚠ Due Soon</span>
{% endif %}
<form method="post" style="display:inline">
    <input type="hidden" name="form_type" value="complete">
    <input type="hidden" name="task_index" value="{{ loop.index0 }}">
    <button class="complete-btn" type="submit">Mark as Completed</button>
</form>
{% if t.notes %}
<div class="notes"><b>Notes:</b> {{ t.notes }}</div>
{% endif %}
<div class="tips">
{% if t.days_left > 7 %}
Plan ahead: break this assignment into smaller steps over the next week.
{% elif t.days_left > 3 %}
Focus on completing a part each day to avoid last-minute stress.
{% else %}
Prioritize this first, stay focused, and avoid distractions.
{% endif %}
</div>
</li>
{% endfor %}
</ul>
</section>

</body>
</html>
"""

TOPIC_GUIDES = {
    "algebra": [
        {"name": "Linear Equations",
         "links": ["https://www.khanacademy.org/math/algebra/linear-equations"],
         "tip": "Practice solving step by step.",
         "quiz": {"question": "Solve: 2x + 5 = 15", "answer": "x = 5"}},
        {"name": "Quadratic Functions",
         "links": ["https://www.khanacademy.org/math/algebra/quadratics"],
         "tip": "Graph and factor to understand roots.",
         "quiz": {"question": "Find the roots of x^2 - 5x + 6 = 0", "answer": "x = 2, 3"}},
        {"name": "Factoring",
         "links": ["https://www.khanacademy.org/math/algebra/factoring"],
         "tip": "Always check your factors by multiplying back.",
         "quiz": {"question": "Factor: x^2 + 7x + 12", "answer": "(x + 3)(x + 4)"}}
    ],
    "photosynthesis": [
        {"name": "Light Reactions",
         "links": ["https://www.khanacademy.org/science/biology/photosynthesis-in-plants"],
         "tip": "Focus on the role of sunlight and water.",
         "quiz": {"question": "What molecule stores energy in light reactions?", "answer": "ATP"}},
        {"name": "Calvin Cycle",
         "links": ["https://www.khanacademy.org/science/biology/photosynthesis-in-plants"],
         "tip": "Pay attention to CO2 fixation.",
         "quiz": {"question": "What is the main sugar produced?", "answer": "Glucose"}}
    ]
}

@app.route("/", methods=["GET", "POST"])
def home():
    guide = None
    error_msg = None

    if request.method == "POST":
        form_type = request.form.get("form_type", "")

        if form_type == "study":
            topics = [t.strip().lower() for t in request.form.get("topics", "").split(",")]
            guide = {}
            for topic in topics:
                if topic:
                    subtopics = TOPIC_GUIDES.get(topic, [
                        {"name": topic.title(),
                         "links": [f"https://www.google.com/search?q={topic.replace(' ','+')}"],
                         "tip": "Review key concepts.",
                         "quiz": None}
                    ])
                    guide[topic.title()] = subtopics

        elif form_type == "task":
            task = request.form.get("task", "")
            due = request.form.get("due", "")
            subject_name = request.form.get("subject_name", "Default")
            priority = request.form.get("priority", "Medium")
            notes = request.form.get("notes", "")

            try:
                datetime.strptime(due, "%Y-%m-%d")
            except ValueError:
                error_msg = f"⚠ Invalid date format: {due}. Please use YYYY-MM-DD."
                return render_template_string(HTML, guide=None, tasks=tasks, error_msg=error_msg,
                                              total_assignments=len(tasks),
                                              completed_assignments=sum(1 for t in tasks if t.get("completed")),
                                              due_soon_count=sum(1 for t in tasks if t.get("due_soon")))

            if task and due:
                tasks.append({"task": task, "due": due, "subject_name": subject_name, "priority": priority, "notes": notes, "completed": False})
                with open(TASKS_FILE, "w") as f:
                    json.dump(tasks, f)
            return redirect(url_for('home'))

        elif form_type == "complete":
            index = int(request.form.get("task_index", -1))
            if 0 <= index < len(tasks):
                tasks[index]["completed"] = True
                with open(TASKS_FILE, "w") as f:
                    json.dump(tasks, f)
            return redirect(url_for('home'))

    today = datetime.today()
    for t in tasks:
        try:
            due_date = datetime.strptime(t["due"], "%Y-%m-%d")
            t["days_left"] = (due_date - today).days
            t["due_soon"] = t["days_left"] <= 3
        except ValueError:
            t["days_left"] = 0
            t["due_soon"] = False

    priority_order = {"High": 1, "Medium": 2, "Low": 3}
    tasks.sort(key=lambda x: (x.get("completed"), datetime.strptime(x["due"], "%Y-%m-%d"), priority_order.get(x.get("priority","Medium"), 2)))

    total_assignments = len(tasks)
    completed_assignments = sum(1 for t in tasks if t.get("completed"))
    due_soon_count = sum(1 for t in tasks if t.get("due_soon") and not t.get("completed"))

    return render_template_string(HTML, guide=guide, tasks=tasks, error_msg=error_msg,
                                  total_assignments=total_assignments,
                                  completed_assignments=completed_assignments,
                                  due_soon_count=due_soon_count)

if __name__ == "__main__":
    app.run(debug=True, port=5001)

