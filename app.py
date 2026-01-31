from flask import Flask, render_template, request, redirect
import sqlite3

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

    cur.execute("""
        SELECT * FROM tasks
        WHERE status = 'pending'
        ORDER BY position ASC
    """)
    tasks = cur.fetchall()

    conn.close()
    return render_template("index.html", tasks=tasks)

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

# -------------------------
# Run app
# -------------------------
if __name__ == "__main__":
    app.run()
