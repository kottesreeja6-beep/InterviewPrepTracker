from flask import Flask, render_template, request, redirect
import sqlite3
app = Flask(__name__)


def create_database():
    connection = sqlite3.connect("tracker.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            role TEXT,
            location TEXT,
            date TEXT,
            status TEXT
        )
    """)
    
    cursor.execute("PRAGMA table_info(applications)")
    columns = [column[1] for column in cursor.fetchall()]

    if "interview_datetime" not in columns:
        cursor.execute(
            "ALTER TABLE applications ADD COLUMN interview_datetime TEXT"
        )

    connection.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        category TEXT,
        answer TEXT
    )
""")

    connection.commit()
    connection.close()


@app.route("/")
def home():

    connection = sqlite3.connect("tracker.db")
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM applications")
    application_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM questions")
    question_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applications WHERE status = 'Interview'")
    interview_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM applications WHERE status = 'Selected'")
    selected_count = cursor.fetchone()[0]

    connection.close()

    return render_template(
        "index.html",
        application_count=application_count,
        interview_count=interview_count,
        selected_count=selected_count,
        question_count=question_count
    )

@app.route("/questions", methods=["GET", "POST"])
def questions():

    if request.method == "POST":

        question = request.form["question"]
        category = request.form["category"]
        answer = request.form["answer"]

        connection = sqlite3.connect("tracker.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO questions
            (question, category, answer)
            VALUES (?, ?, ?)
        """, (question, category, answer))

        connection.commit()
        connection.close()

    connection = sqlite3.connect("tracker.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM questions")
    questions_data = cursor.fetchall()

    connection.close()

    return render_template(
        "questions.html",
        questions=questions_data
    )
    
@app.route("/skills")
def skills():
    return render_template("skills.html") 


@app.route("/applications", methods=["GET", "POST"])


@app.route("/applications", methods=["GET", "POST"])
def applications():

    connection = sqlite3.connect("tracker.db")
    cursor = connection.cursor()

    if request.method == "POST":
        company = request.form["company"]
        role = request.form["role"]
        location = request.form["location"]
        date = request.form["date"]
        interview_datetime = request.form.get("interview_datetime", "")
        status = request.form["status"]

        cursor.execute("""
            INSERT INTO applications
            (company, role, location, date, status, interview_datetime)
            VALUES (?, ?, ?, ?, ?,?)
        """, (company, role, location, date, status,interview_datetime))

        connection.commit()

    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()

    query = "SELECT * FROM applications WHERE company LIKE ?"
    params = ["%" + search + "%"]

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    cursor.execute(query, params)
    applications_data = cursor.fetchall()

    connection.close()

    return render_template(
        "applications.html",
        applications=applications_data,
        search=search,
        status_filter=status_filter
    )

@app.route("/delete/<int:application_id>")
@app.route("/delete-question/<int:question_id>")
def delete_question(question_id):

    connection = sqlite3.connect("tracker.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM questions WHERE id = ?",
        (question_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/questions")
def delete_application(application_id):

    connection = sqlite3.connect("tracker.db")
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM applications WHERE id = ?",
        (application_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/applications")



@app.route("/edit/<int:application_id>", methods=["GET", "POST"])
def edit_application(application_id):

    connection = sqlite3.connect("tracker.db")
    cursor = connection.cursor()

    if request.method == "POST":
        company = request.form["company"]
        role = request.form["role"]
        location = request.form["location"]
        date = request.form["date"]
        status = request.form["status"]
        interview_datetime = request.form.get("interview_datetime", "")

        cursor.execute("""
            UPDATE applications
            SET company = ?, role = ?, location = ?, date = ?,
                status = ?, interview_datetime = ?
            WHERE id = ?
        """, (
            company,
            role,
            location,
            date,
            status,
            interview_datetime,
            application_id
        ))

        connection.commit()
        connection.close()
        return redirect("/applications")

    cursor.execute(
        "SELECT * FROM applications WHERE id = ?",
        (application_id,)
    )

    application = cursor.fetchone()
    connection.close()

    if application is None:
        return redirect("/applications")

    return render_template(
        "edit.html",
        application=application
    )

    
    
@app.route("/edit-question/<int:question_id>", methods=["GET", "POST"])
def edit_question(question_id):

    connection = sqlite3.connect("tracker.db")
    cursor = connection.cursor()

    if request.method == "POST":
        question_text = request.form["question"]
        category = request.form["category"]
        answer = request.form["answer"]

        cursor.execute("""
            UPDATE questions
            SET question = ?, category = ?, answer = ?
            WHERE id = ?
        """, (question_text, category, answer, question_id))

        connection.commit()
        connection.close()

        return redirect("/questions")

    cursor.execute(
        "SELECT * FROM questions WHERE id = ?",
        (question_id,)
    )

    question = cursor.fetchone()
    connection.close()

    if question is None:
        return redirect("/questions")

    return render_template(
        "edit_question.html",
        question=question
    )


create_database()


import os

if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))