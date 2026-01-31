from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("tick_it_focus.db")
    conn.row_factory = sqlite3.Row
    return conn

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

if __name__ == "__main__":
    app.run()
