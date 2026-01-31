from flask import Flask, render_template, request, redirect
import sqlite3
from flask import jsonify


app = Flask(__name__)

# -------------------------
# Database helper
# -------------------------
def get_db():
    conn = sqlite3.connect("tick_it_focus.db")
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------
# Home page - show tasks
# -------------------------
@app.route("/")
def index():
    conn = get_db()
    cur = conn.cursor()

    # Fetch pending tasks
    cur.execute("""
        SELECT * FROM tasks
        WHERE status = 'pending'
        ORDER BY position ASC
    """)
    pending_rows = cur.fetchall()

    # Fetch completed tasks
    cur.execute("""
        SELECT * FROM tasks
        WHERE status = 'completed'
        ORDER BY completed_at DESC
    """)
    completed_rows = cur.fetchall()

    conn.close()

    # ✅ Convert sqlite Row objects to dicts
    pending_tasks = [dict(row) for row in pending_rows]
    completed_tasks = [dict(row) for row in completed_rows]

    return render_template(
        "index.html",
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks
    )

# -------------------------
# Add new task
# -------------------------
@app.route("/add-task", methods=["POST"])
def add_task():
    title = request.form["title"]
    description = request.form["description"]
    focus_minutes = int(request.form["focus_minutes"])

    conn = get_db()
    cur = conn.cursor()

    # determine next task position
    cur.execute("SELECT COUNT(*) FROM tasks")
    position = cur.fetchone()[0] + 1

    cur.execute("""
        INSERT INTO tasks (title, description, focus_minutes, position)
        VALUES (?, ?, ?, ?)
    """, (title, description, focus_minutes, position))

    conn.commit()
    conn.close()

    return redirect("/")
@app.route("/complete-task/<int:task_id>")
def complete_task(task_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE tasks
        SET status = 'completed',
            completed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()

    return redirect("/")
@app.route("/api/complete-task", methods=["POST"])
def api_complete_task():
    data = request.get_json()
    task_id = data.get("task_id")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE tasks
        SET status = 'completed',
            completed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()

    return jsonify({"success": True})


# -------------------------
# Run app
# -------------------------
if __name__ == "__main__":
    app.run()
