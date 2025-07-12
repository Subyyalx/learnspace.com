from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
from flask import send_from_directory

app = Flask(__name__)
BASE_PATH = r"E:\DevOps\AWS Certified Solutions Architect Professional" # Adjust this path to your course directory
VIDEO_EXTENSIONS = (".mp4", ".mkv", ".mov", ".avi")
DB_FILE = "progress.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                lecture_id TEXT PRIMARY KEY
            )
        ''')
        conn.commit()

def get_completed_lectures():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT lecture_id FROM progress")
        return set(row[0] for row in c.fetchall())

def mark_completed(lecture_id):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO progress (lecture_id) VALUES (?)", (lecture_id,))
        conn.commit()

def get_course_structure():
    sections = []
    for section_index, section_name in enumerate(sorted(os.listdir(BASE_PATH))):
        section_path = os.path.join(BASE_PATH, section_name)
        if os.path.isdir(section_path):
            lectures = []
            for lecture_index, file_name in enumerate(sorted(os.listdir(section_path))):
                if file_name.lower().endswith(VIDEO_EXTENSIONS):
                    lecture_id = f"{section_name}/{file_name}"
                    collapse_id = f"preview-{section_index}-{lecture_index}"
                    lectures.append({
                        "title": file_name,
                        "id": lecture_id,
                        "collapse_id": collapse_id
                    })
            if lectures:
                sections.append({
                    "name": section_name,
                    "lectures": lectures
                })
    return sections


@app.route("/")
def index():
    course = get_course_structure()
    completed = get_completed_lectures()
    total = sum(len(sec["lectures"]) for sec in course)
    done = len(completed)
    progress = int((done / total) * 100) if total else 0
    return render_template("index.html", course=course, completed=completed, progress=progress)

@app.route("/complete", methods=["POST"])
def complete():
    lecture_id = request.form["lecture_id"]
    mark_completed(lecture_id)
    return redirect(url_for("index"))
@app.route('/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory(BASE_PATH, filename)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
