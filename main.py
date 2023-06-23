
import os
from flask import Flask, render_template, request
import sqlite3


###---  Constants  ---###
STUDENTS_DB = 'students.db'


def reset_db():
    conn = sqlite3.connect(STUDENTS_DB)
    c = conn.cursor()
    # c.execute('DROP TABLE IF EXISTS students')
    c.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        year_of_birth INTEGER,
        course TEXT);''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS grades (
        student_id INTEGER,
        subject TEXT,
        grade INTEGER,
        FOREIGN KEY (student_id) REFERENCES students(id)
    );''')
    conn.commit()
    conn.close()


def is_in_db(c, condition):
    conn = sqlite3.connect(STUDENTS_DB)
    c.execute(f'SELECT * FROM students WHERE {condition}')
    result = c.fetchall()
    conn.close()
    return len(result) > 0


def get_id_from_name(name):
    conn = sqlite3.connect(STUDENTS_DB)
    c = conn.cursor()
    c.execute('SELECT id FROM students WHERE name = ?', (name,))
    result = c.fetchone()
    conn.close()
    return result[0]


###---  Entry point  ---###

app = Flask('ScholarshipManagementSystem')


# Index
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


# Add student
@app.route('/add_student_form', methods=['GET'])
def add_student_form():
    return render_template('add_student_form.html')

@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form.get('name')
    year_of_birth = request.form.get('year_of_birth')
    course = request.form.get('course')
    conn = sqlite3.connect(STUDENTS_DB)
    c = conn.cursor()
    c.execute('INSERT INTO students (name, year_of_birth, course) VALUES (?, ?, ?)', (name, year_of_birth, course))
    conn.commit()
    conn.close()
    return '<script>alert("Student added!"); window.location.href = "/";</script>'


# Delete student
@app.route('/delete_student', methods=['POST'])
def delete_student():
    name = request.form.get('name')
    conn = sqlite3.connect(STUDENTS_DB)
    c = conn.cursor()
    c.execute('DELETE FROM students WHERE name = ?', (name,))
    conn.commit()
    conn.close()
    return f'<script>alert("Student {name} deleted!"); window.location.href = "/";</script>'


# Manage grades
@app.route('/manage_grades', methods=['GET'])
def manage_grades():
    return render_template('manage_grades.html')


# Add grade
@app.route('/add_grade', methods=['POST'])
def add_grade():
    conn = sqlite3.connect(STUDENTS_DB)
    c = conn.cursor()

    student_name = request.form.get('name')
    if not is_in_db(c, f'name = "{student_name}"'):
        return f'<script>alert("Student "{student_name}" not found!"); window.location.href = "/add_grade";</script>'
    student_id = get_id_from_name(student_name)

    subject = request.form.get('subject')
    grade = request.form.get('grade')
    c.execute('INSERT INTO grades (student_id, subject, grade) VALUES (?, ?, ?)', (student_id, subject, grade))
    conn.commit()
    conn.close()
    return '<script>alert("Grade added!"); window.location.href = "/";</script>'

# Edit grade
@app.route('/edit_grade', methods=['POST'])
def edit_grade():
    student_name = request.form.get('name')
    student_id = get_id_from_name(student_name)
    subject = request.form.get('subject')
    old_grade = request.form.get('old_grade')
    new_grade = request.form.get('new_grade')

    conn = sqlite3.connect(STUDENTS_DB)
    c = conn.cursor()
    if not is_in_db(c, f'student_id = "{student_id}" AND subject = "{subject}" AND grade = {old_grade}'):
        return '<script>alert("Entry not found!"); window.location.href = "/edit_grade";</script>'

    c.execute('UPDATE grades SET grade = ? WHERE student_id = "?" AND subject = "?" AND grade = ?', (new_grade, student_id, subject, old_grade))
    conn.commit()
    conn.close()
    return '<script>alert("Grade edited!"); window.location.href = "/";</script>'


# List all students
@app.route('/show_students')
def show_students():
    conn = sqlite3.connect(STUDENTS_DB)
    c = conn.cursor()
    c.execute('SELECT * FROM students')
    students = c.fetchall()
    conn.close()
    return render_template('show_students.html', students=students)



if __name__ == '__main__':
    reset_db()
    app.run()

