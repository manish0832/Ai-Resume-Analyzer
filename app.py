import os
import json
import tempfile
import datetime
from flask import Flask, render_template, request, jsonify, send_file, session, redirect
from werkzeug.utils import secure_filename

from utils.extract_text import extract_text_from_file
from utils.ats_score import calculate_ats_score, analyze_skills_match
from utils.optimizer import generate_suggestions, create_optimized_resume
import mysql.connector

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "admin_secret_key_123")

# Upload limits & config
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'temp_uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="manish",
        password="1234",
        database="manish0832"
    )




def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# HOME PAGE
@app.route('/')
def index():
    return render_template('index.html')


# RESUME ANALYSIS
@app.route('/analyze', methods=['POST'])
def analyze_resume():
    try:
        job_description = request.form.get('job_description', '').strip()
        if not job_description:
            return jsonify({'error': 'Job description is required'}), 400

        if 'resume_file' not in request.files:
            return jsonify({'error': 'No resume file uploaded'}), 400

        file = request.files['resume_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            resume_text = extract_text_from_file(filepath)

            if not resume_text or not resume_text.strip():
                return jsonify({'error': 'Could not extract text'}), 400

            ats_score = calculate_ats_score(resume_text, job_description)
            skills_analysis = analyze_skills_match(resume_text, job_description)
            suggestions = generate_suggestions(resume_text, job_description, skills_analysis)

            # Save to DB
            db = get_db_connection()
            cursor = db.cursor()
            try:
                cursor.execute("""
                    INSERT INTO resume_analysis
                    (filename, job_description, resume_text, ats_score, matched_skills,
                     missing_skills, skill_match_percentage, suggestions, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, (
                    filename,
                    job_description,
                    resume_text,
                    ats_score,
                    json.dumps(skills_analysis.get('matched_skills', [])),
                    json.dumps(skills_analysis.get('missing_skills', [])),
                    skills_analysis.get('match_percentage', 0),
                    json.dumps(suggestions)
                ))

                db.commit()
                resume_id = cursor.lastrowid
            finally:
                cursor.close()
                db.close()

            results = {
                'id': resume_id,
                'ats_score': ats_score,
                'skill_match_percentage': skills_analysis.get('match_percentage', 0),
                'matched_skills': skills_analysis.get('matched_skills', []),
                'missing_skills': skills_analysis.get('missing_skills', []),
                'suggestions': suggestions,
                'resume_text': (resume_text[:500] + '...') if len(resume_text) > 500 else resume_text
            }

            return render_template('result.html', results=results, job_description=job_description)

        finally:
            # cleanup uploaded file
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception:
                    pass

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# DOWNLOAD OPTIMIZED RESUME
@app.route('/download-optimized', methods=['POST'])
def download_optimized_resume():
    try:
        data = request.get_json(force=True)
        resume_text = data.get('resume_text')
        suggestions = data.get('suggestions', [])
        resume_id = data.get('resume_id')

        if not resume_text:
            return jsonify({'error': 'Resume text missing'}), 400

        if not resume_id:
            return jsonify({'error': 'Resume ID missing'}), 400

        # create_optimized_resume should return a path to a .docx file (existing on disk)
        optimized_file_path = create_optimized_resume(resume_text, suggestions)
        if not optimized_file_path or not os.path.exists(optimized_file_path):
            return jsonify({'error': 'Could not generate optimized resume'}), 500

        # Log download
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO download_logs (resume_id, download_time) VALUES (%s, NOW())",
                (resume_id,)
            )
            db.commit()
        finally:
            cursor.close()
            db.close()

        return send_file(
            optimized_file_path,
            as_attachment=True,
            download_name="optimized_resume.docx",
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -----------------------
# ADMIN ROUTES
# -----------------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute(
                "SELECT id FROM admin WHERE username=%s AND password=%s",
                (username, password)
            )
            admin = cursor.fetchone()
        finally:
            cursor.close()
            db.close()

        if admin:
            session['admin'] = username
            return redirect("/admin/dashboard")
        else:
            return render_template("admin_login.html", error="Invalid username or password")

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    if 'admin' not in session:
        return redirect("/admin/login")

    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM resume_analysis")
        total_resumes = cursor.fetchone()[0] or 0

        cursor.execute("SELECT AVG(ats_score) FROM resume_analysis")
        avg_ats_score = cursor.fetchone()[0] or 0

        cursor.execute("SELECT AVG(skill_match_percentage) FROM resume_analysis")
        avg_skill_match = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT DATE(created_at), ats_score, skill_match_percentage
            FROM resume_analysis
            ORDER BY created_at DESC
            LIMIT 10
        """)
        rows = cursor.fetchall()
    finally:
        cursor.close()
        db.close()

    # Prepare chart data (reverse oldest->newest)
    dates = [str(row[0]) for row in rows][::-1]
    ats_scores = [row[1] for row in rows][::-1]
    skill_matches = [row[2] for row in rows][::-1]

    stats = {
        "total_resumes": total_resumes,
        "avg_ats_score": round(float(avg_ats_score or 0), 2),
        "avg_skill_match": round(float(avg_skill_match or 0), 2),
        "dates": dates,
        "ats_scores": ats_scores,
        "skill_matches": skill_matches
    }

    return render_template("admin_dashboard.html", stats=stats)


@app.route("/admin/logout")
def admin_logout():
    session.pop('admin', None)
    return redirect("/admin/login")


@app.route("/admin")
def admin_home():
    return redirect("/admin/login")


@app.route("/admin/history")
def admin_history():
    if 'admin' not in session:
        return redirect("/admin/login")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM resume_analysis ORDER BY created_at DESC")
        history = cursor.fetchall()
    finally:
        cursor.close()
        db.close()

    return render_template("admin_history.html", history=history)


@app.route("/admin/history/view/<int:record_id>")
def admin_history_view(record_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM resume_analysis WHERE id=%s", (record_id,))
        data = cursor.fetchone()
    finally:
        cursor.close()
        db.close()

    if not data:
        return "Record not found", 404

    return render_template("admin_view.html", data=data)


@app.route("/admin/history/download/<int:record_id>")
def admin_history_download(record_id):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT resume_text, filename FROM resume_analysis WHERE id=%s", (record_id,))
        row = cursor.fetchone()
    finally:
        cursor.close()
        db.close()

    if not row:
        return "Record not found", 404

    text, filename = row
    # create a safe temporary file and return it
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", prefix=f"download_{record_id}_", dir=".")
    try:
        tmp.write(text.encode('utf-8'))
        tmp.flush()
        tmp.close()
        return send_file(tmp.name, as_attachment=True, download_name=f"{filename}.txt", mimetype="text/plain")
    finally:
        # schedule removal (do not remove immediately; returned file must be read by client)
        # optionally: use a background cleaner or remove after some time.
        pass


@app.route("/admin/history/update/<int:record_id>", methods=["GET", "POST"])
def admin_history_update(record_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        new_job = request.form.get("job_description", "")
        new_text = request.form.get("resume_text", "")

        try:
            cursor.execute("""
                UPDATE resume_analysis
                SET job_description=%s, resume_text=%s
                WHERE id=%s
            """, (new_job, new_text, record_id))
            db.commit()
        finally:
            cursor.close()
            db.close()

        return redirect("/admin/history")

    try:
        cursor.execute("SELECT * FROM resume_analysis WHERE id=%s", (record_id,))
        data = cursor.fetchone()
    finally:
        cursor.close()
        db.close()

    if not data:
        return "Record not found", 404

    return render_template("admin_update.html", data=data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
