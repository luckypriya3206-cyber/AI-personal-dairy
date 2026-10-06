from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

DATABASE = "diary.db"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================= DATABASE =================

def create_database():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            mood TEXT NOT NULL,
            date TEXT NOT NULL,
            photo TEXT
        )
    """)

    cursor.execute("PRAGMA table_info(diary)")
    columns = [column[1] for column in cursor.fetchall()]

    if "photo" not in columns:
        cursor.execute(
            "ALTER TABLE diary ADD COLUMN photo TEXT"
        )

    conn.commit()
    conn.close()


# ================= GET ENTRIES =================

def get_entries():

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM diary
        ORDER BY id DESC
    """)

    entries = cursor.fetchall()

    conn.close()

    return entries


# ================= HOME =================

@app.route("/")
def home():

    entries = get_entries()

    return render_template(
        "index.html",
        entries=entries
    )


# ================= SAVE DIARY =================

@app.route("/save", methods=["POST"])
def save():

    title = request.form["title"]
    content = request.form["content"]
    mood = request.form["mood"]

    photo = request.files.get("photo")

    photo_filename = None

    if photo and photo.filename:

        photo_filename = secure_filename(
            photo.filename
        )

        photo.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                photo_filename
            )
        )

    date = datetime.now().strftime(
        "%d-%m-%Y %I:%M %p"
    )

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO diary
        (title, content, mood, date, photo)
        VALUES (?, ?, ?, ?, ?)
    """, (
        title,
        content,
        mood,
        date,
        photo_filename
    ))

    conn.commit()
    conn.close()

    return redirect("/")


# ================= CHATBOT =================

@app.route("/chat", methods=["POST"])
def chat():

    message = request.form["message"].lower()

    if "hello" in message or "hi" in message:

        reply = "Hello! 👋 How was your day?"

    elif "happy" in message:

        reply = (
            "That's wonderful! 😊 "
            "I'm glad you had a happy day."
        )

    elif "sad" in message:

        reply = (
            "I'm sorry you're feeling sad. 💙 "
            "You can write your thoughts in your diary."
        )

    elif "angry" in message:

        reply = (
            "It sounds like something bothered you. "
            "Take some time to relax."
        )

    elif "excited" in message:

        reply = (
            "That's great! 🤩 "
            "Tell me what made you excited today."
        )

    elif "good" in message:

        reply = (
            "I'm happy to hear that! "
            "What was the best part of your day?"
        )

    elif "bad" in message:

        reply = (
            "I'm sorry you had a difficult day. "
            "You can write about it in your diary."
        )

    elif "thank" in message:

        reply = "You're welcome! 😊"

    elif "diary" in message:

        reply = (
            "Your diary is a place to record "
            "your thoughts, feelings and memories."
        )

    else:

        reply = (
            "I understand. Tell me more about "
            "your day. I'm listening. 😊"
        )

    return reply


# ================= SUGGESTIONS =================

@app.route("/suggest", methods=["POST"])
def suggest():

    thought = request.form.get(
        "thought",
        ""
    ).lower()

    if "stress" in thought or "stressed" in thought:

        suggestion = (
            "You seem to be feeling stressed. "
            "Try taking a short break and handle "
            "your tasks one at a time."
        )

    elif "sad" in thought or "upset" in thought:

        suggestion = (
            "It sounds like you are having a difficult day. "
            "Writing your feelings down can help."
        )

    elif "happy" in thought or "good" in thought:

        suggestion = (
            "You had a positive day! "
            "Remember what made you happy and keep "
            "doing things that help you feel good."
        )

    elif "exam" in thought or "study" in thought:

        suggestion = (
            "Try creating a simple study schedule. "
            "Focus on one topic at a time and take short breaks."
        )

    elif "college" in thought or "class" in thought:

        suggestion = (
            "Keep noting your college experiences "
            "and what you learned today."
        )

    elif "friend" in thought:

        suggestion = (
            "Friendships can make college life memorable. "
            "Spend some quality time with people "
            "you feel comfortable with."
        )

    elif "tired" in thought or "busy" in thought:

        suggestion = (
            "You seem to have had a busy day. "
            "Make some time to rest and organize "
            "tomorrow's tasks."
        )

    else:

        suggestion = (
            "Keep writing your thoughts regularly. "
            "Reflect on what went well today and "
            "what you would like to improve tomorrow."
        )

    return suggestion


# ================= START APPLICATION =================

if __name__ == "__main__":

    create_database()

    app.run(debug=True)