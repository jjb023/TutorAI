# web/app.py
from flask import Flask, render_template, request, redirect, url_for
import sys
import os

# Add the parent directory to the path so we can import our database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import TutorAIDatabase

# Create Flask app with static folder specified
app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'your-secret-key-change-this-later'

# Database connection function (creates new connection for each request)
def get_db():
    """Get a new database connection for each request"""
    return TutorAIDatabase("../data/tutor_ai.db")

@app.route('/')
def home():
    """Home page - shows basic info"""
    db = get_db()
    students = db.get_all_students()
    tutors = db.get_all_tutors()
    db.close()
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tutor AI - Dashboard</title>
        <link rel="stylesheet" href="/static/style.css">
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎯</text></svg>">
    </head>
    <body>
        <div class="container">
            <h1>🎯 Tutor AI Dashboard</h1>
            
            <div style="display: flex; justify-content: center; gap: 30px; margin: 30px 0; flex-wrap: wrap;">
                <div class="stats-card">
                    <div class="stats-icon">📚</div>
                    <div class="stats-number">{len(students)}</div>
                    <div class="stats-label">Students</div>
                </div>
                <div class="stats-card">
                    <div class="stats-icon">👥</div>
                    <div class="stats-number">{len(tutors)}</div>
                    <div class="stats-label">Tutors</div>
                </div>
                <div class="stats-card">
                    <div class="stats-icon">✅</div>
                    <div class="stats-number">MVP</div>
                    <div class="stats-label">Status</div>
                </div>
            </div>
            
            <div class="nav-links">
                <a href="/students" class="btn">📚 View All Students</a>
                <a href="/add-student" class="btn btn-success">➕ Add New Student</a>
                <a href="/tutors" class="btn btn-warning">👥 View All Tutors</a>
            </div>
            
            <div class="welcome-message">
                <p>✨ Your professional tutor management system is ready!</p>
                <p style="font-size: 0.9em; opacity: 0.8;">Track progress • Generate insights • Manage sessions</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/students')
def students_list():
    """Show all students"""
    db = get_db()
    students = db.get_all_students()
    
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>All Students - Tutor AI</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <h1>📚 All Students</h1>
    """
    
    if not students:
        html += """
            <div class="welcome-message">
                <p>No students in database yet.</p>
                <a href="/add-student" class="btn btn-success">➕ Add your first student</a>
            </div>
        """
    else:
        html += f'<p style="text-align: center; font-size: 1.2em; color: #666; margin-bottom: 30px;">Managing <strong>{len(students)}</strong> students</p>'
        html += '<div class="student-grid">'
        
        for student in students:
            id, name, age, year, school, contact, notes, created, last_session = student
            
            html += f"""
            <div class="student-card">
                <h3>🎓 {name}</h3>
                <div style="margin: 15px 0;">
                    <p><strong>Age:</strong> {age} | <strong>Year:</strong> {year}</p>
                    {f'<p><strong>School:</strong> {school}</p>' if school else ''}
                    {f'<p style="color: #27ae60;"><strong>Last Session:</strong> {last_session}</p>' if last_session else '<p style="color: #95a5a6;"><em>No sessions yet</em></p>'}
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 15px;">
                    <a href="/student/{id}" class="btn" style="flex: 1; min-width: 120px; text-align: center;">📊 Progress</a>
                    <a href="/session/{id}" class="btn btn-success" style="flex: 1; min-width: 120px; text-align: center;">⚡ Session</a>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">
                    <a href="/edit-student/{id}" class="btn btn-warning" style="flex: 1; text-align: center;">✏️ Edit</a>
                    <a href="/delete-student/{id}" onclick="return confirm('Are you sure you want to delete {name}?')" class="btn btn-danger" style="flex: 1; text-align: center;">🗑️ Delete</a>
                </div>
            </div>
            """
        
        html += '</div>'
    
    html += """
            <div class="nav-links">
                <a href="/add-student" class="btn btn-success">➕ Add New Student</a>
                <a href="/">🏠 Back to Dashboard</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    db.close()
    return html

@app.route('/edit-student/<int:student_id>')
def edit_student_form(student_id):
    """Show form to edit student details"""
    db = get_db()
    students = db.get_all_students()
    student = None
    for s in students:
        if s[0] == student_id:
            student = s
            break
    
    if not student:
        db.close()
        return f"<h1>❌ Student not found</h1><p><a href='/students'>Back to students</a></p>"
    
    id, name, age, year, school, contact, notes, created, last_session = student
    
    html = f"""
    <h1>✏️ Edit Student: {name}</h1>
    <form method="POST" action="/update-student/{student_id}">
        <div style="margin: 20px 0; max-width: 500px;">
            <div style="margin: 15px 0;">
                <label style="display: block; margin-bottom: 5px;"><strong>Student Name:</strong></label>
                <input type="text" name="name" value="{name}" required style="width: 100%; padding: 8px; font-size: 16px;">
            </div>
            
            <div style="margin: 15px 0;">
                <label style="display: block; margin-bottom: 5px;"><strong>Age:</strong></label>
                <input type="number" name="age" value="{age}" min="4" max="18" required style="width: 100%; padding: 8px; font-size: 16px;">
            </div>
            
            <div style="margin: 15px 0;">
                <label style="display: block; margin-bottom: 5px;"><strong>Year Group:</strong></label>
                <select name="year_group" required style="width: 100%; padding: 8px; font-size: 16px;">
                    <option value="Year 3" {"selected" if year == "Year 3" else ""}>Year 3</option>
                    <option value="Year 4" {"selected" if year == "Year 4" else ""}>Year 4</option>
                    <option value="Year 5" {"selected" if year == "Year 5" else ""}>Year 5</option>
                    <option value="Year 6" {"selected" if year == "Year 6" else ""}>Year 6</option>
                </select>
            </div>
            
            <div style="margin: 15px 0;">
                <label style="display: block; margin-bottom: 5px;"><strong>Target School:</strong></label>
                <input type="text" name="target_school" value="{school or ''}" style="width: 100%; padding: 8px; font-size: 16px;">
            </div>
            
            <div style="margin: 15px 0;">
                <label style="display: block; margin-bottom: 5px;"><strong>Parent Contact:</strong></label>
                <input type="text" name="parent_contact" value="{contact or ''}" style="width: 100%; padding: 8px; font-size: 16px;">
            </div>
            
            <div style="margin: 15px 0;">
                <label style="display: block; margin-bottom: 5px;"><strong>Notes:</strong></label>
                <textarea name="notes" rows="3" style="width: 100%; padding: 8px; font-size: 16px;">{notes or ''}</textarea>
            </div>
            
            <button type="submit" style="background: #4CAF50; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 16px; margin-top: 10px;">
                💾 Update Student
            </button>
        </div>
    </form>
    
    <hr>
    <p><a href="/student/{student_id}">📊 View Progress</a> | <a href="/students">📚 All Students</a> | <a href="/">🏠 Home</a></p>
    """
    
    db.close()
    return html

@app.route('/update-student/<int:student_id>', methods=['POST'])
def update_student(student_id):
    """Update student information"""
    db = get_db()
    
    # Get form data
    name = request.form.get('name', '').strip()
    age = request.form.get('age')
    year_group = request.form.get('year_group', '').strip()
    target_school = request.form.get('target_school', '').strip() or None
    parent_contact = request.form.get('parent_contact', '').strip() or None
    notes = request.form.get('notes', '').strip() or None
    
    # Update in database
    query = """
    UPDATE students 
    SET name = ?, age = ?, year_group = ?, target_school = ?, parent_contact = ?, notes = ?
    WHERE id = ?
    """
    
    try:
        db.cursor.execute(query, (name, int(age), year_group, target_school, parent_contact, notes, student_id))
        db.connection.commit()
        
        html = f"""
        <h1>✅ Student Updated Successfully!</h1>
        <p><strong>Student:</strong> {name} has been updated.</p>
        
        <div style="margin: 20px 0;">
            <p><a href="/student/{student_id}">📊 View {name}'s Progress</a></p>
            <p><a href="/students">📚 All Students</a></p>
            <p><a href="/">🏠 Home</a></p>
        </div>
        """
    except Exception as e:
        html = f"""
        <h1>❌ Error Updating Student</h1>
        <p>Error: {e}</p>
        <p><a href="/edit-student/{student_id}">Try again</a></p>
        """
    
    db.close()
    return html

@app.route('/delete-student/<int:student_id>')
def delete_student(student_id):
    """Delete student and all their progress"""
    db = get_db()
    
    # Get student name first
    students = db.get_all_students()
    student_name = "Student"
    for s in students:
        if s[0] == student_id:
            student_name = s[1]
            break
    
    try:
        # Delete student progress first (foreign key constraint)
        db.cursor.execute("DELETE FROM subtopic_progress WHERE student_id = ?", (student_id,))
        # Delete sessions
        db.cursor.execute("DELETE FROM sessions WHERE student_id = ?", (student_id,))
        # Delete student
        db.cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        db.connection.commit()
        
        html = f"""
        <h1>✅ Student Deleted</h1>
        <p><strong>{student_name}</strong> and all their progress data has been removed.</p>
        
        <div style="margin: 20px 0;">
            <p><a href="/students">📚 All Students</a></p>
            <p><a href="/">🏠 Home</a></p>
        </div>
        """
    except Exception as e:
        html = f"""
        <h1>❌ Error Deleting Student</h1>
        <p>Error: {e}</p>
        <p><a href="/students">Back to students</a></p>
        """
    
    db.close()
    return html

@app.route('/tutors')
def tutors_list():
    """Show all tutors"""
    db = get_db()
    tutors = db.get_all_tutors()
    
    html = "<h1>👥 All Tutors</h1>"
    
    if tutors:
        html += f"<p>Total tutors: {len(tutors)}</p>"
        for tutor in tutors:
            id, username, full_name, email, last_login = tutor
            html += f"""
            <div style='border: 1px solid #ccc; padding: 15px; margin: 10px 0; border-radius: 8px;'>
                <h3>👤 {full_name}</h3>
                <p><strong>Username:</strong> {username}</p>
                {f'<p><strong>Email:</strong> {email}</p>' if email else ''}
                {f'<p><strong>Last Login:</strong> {last_login}</p>' if last_login else '<p><em>Never logged in</em></p>'}
            </div>
            """
    else:
        html += "<p>No tutors found.</p>"
    
    html += '<p><a href="/">🏠 Back to Home</a></p>'
    db.close()
    return html

@app.route('/student/<int:student_id>')
def student_detail(student_id):
    """Show detailed progress for a specific student"""
    db = get_db()
    
    # Get student info
    students = db.get_all_students()
    student = None
    for s in students:
        if s[0] == student_id:
            student = s
            break
    
    if not student:
        db.close()
        return f"<h1>❌ Student not found</h1><p><a href='/students'>Back to students</a></p>"
    
    name = student[1]
    
    # Get progress summary
    summary = db.get_student_main_topic_summary(student_id)
    
    html = f"<h1>📊 Progress Report: {name}</h1>"
    
    if not any(row[3] > 0 for row in summary):  # Check if any subtopics assessed
        html += "<p>No progress recorded yet.</p>"
        html += f'<p><a href="/session/{student_id}">⚡ Start first assessment</a></p>'
    else:
        html += "<div style='margin: 20px 0;'>"
        for topic_name, color, total_subs, assessed_subs, avg_mastery, completion_pct in summary:
            if assessed_subs > 0:
                # Color code based on average mastery
                if avg_mastery >= 7:
                    status = "🟢"
                elif avg_mastery >= 4:
                    status = "🟡"
                else:
                    status = "🔴"
                
                html += f"""
                <div style='border: 1px solid #ccc; padding: 15px; margin: 10px 0; border-radius: 8px;'>
                    <h3>{status} {topic_name}</h3>
                    <p><strong>Completion:</strong> {completion_pct}%</p>
                    <p><strong>Average Mastery:</strong> {avg_mastery}/10</p>
                    <p><strong>Assessed:</strong> {assessed_subs}/{total_subs} subtopics</p>
                </div>
                """
        html += "</div>"
    
    html += f"""
    <hr>
    <p>
        <a href="/session/{student_id}">⚡ Quick Session Entry</a> | 
        <a href="/students">📚 All Students</a> | 
        <a href="/">🏠 Home</a>
    </p>
    """
    
    db.close()
    return html

@app.route('/session/<int:student_id>')
def session_entry_form(student_id):
    """Show session entry form for a student"""
    db = get_db()
    
    # Get student info
    students = db.get_all_students()
    student = None
    for s in students:
        if s[0] == student_id:
            student = s
            break
    
    if not student:
        db.close()
        return f"<h1>❌ Student not found</h1><p><a href='/students'>Back to students</a></p>"
    
    name = student[1]
    
    # Get available subtopics
    query = """
    SELECT s.id, s.subtopic_name, mt.topic_name, COALESCE(sp.mastery_level, 0)
    FROM subtopics s
    JOIN main_topics mt ON s.main_topic_id = mt.id
    LEFT JOIN subtopic_progress sp ON s.id = sp.subtopic_id AND sp.student_id = ?
    ORDER BY mt.topic_name, s.difficulty_order
    """
    
    db.cursor.execute(query, (student_id,))
    subtopics = db.cursor.fetchall()
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Session Entry: {name} - Tutor AI</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <h1>⚡ Session Entry: {name}</h1>
            
            <div class="session-container">
                <form method="POST" action="/save-session/{student_id}">
    """
    
    current_topic = ""
    for sub_id, sub_name, topic_name, current_level in subtopics:
        if topic_name != current_topic:
            if current_topic:  # Close previous topic section
                html += "</div>"
            html += f"""
                <div class="topic-section">
                    <h3>📖 {topic_name}</h3>
            """
            current_topic = topic_name
        
        reset_button = f'<button type="button" onclick="resetSubtopic(this)" class="btn btn-danger" style="padding: 5px 10px; font-size: 12px;">Reset</button>' if current_level > 0 else ''
        
        html += f"""
        <div class="subtopic-item">
            <div class="subtopic-label">{sub_name}</div>
            <div class="slider-container">
                <input type="range" name="subtopic_{sub_id}" min="0" max="10" value="{current_level}" 
                       class="slider" id="slider_{sub_id}"
                       oninput="updateScore(this, 'score_{sub_id}')">
                <div class="score-display" id="score_{sub_id}">
                    {'Not assessed' if current_level == 0 else str(current_level) + '/10'}
                </div>
                {reset_button}
            </div>
        </div>
        """
    
    html += """
                </div>
                
                <div style="text-align: center; margin: 40px 0;">
                    <button type="submit" class="btn btn-success" style="font-size: 1.2em; padding: 15px 40px;">
                        💾 Save Session Progress
                    </button>
                </div>
            </form>
            </div>
            
            <div class="nav-links">
                <a href="/students">📚 All Students</a>
                <a href="/">🏠 Dashboard</a>
            </div>
        </div>
        
        <script>
        function updateScore(slider, scoreId) {
            const value = slider.value;
            const scoreDisplay = document.getElementById(scoreId);
            scoreDisplay.textContent = value === '0' ? 'Not assessed' : value + '/10';
            
            // Update color based on score
            if (value >= 8) {
                scoreDisplay.style.background = 'linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)';
            } else if (value >= 5) {
                scoreDisplay.style.background = 'linear-gradient(135deg, #f39c12 0%, #e67e22 100%)';
            } else if (value > 0) {
                scoreDisplay.style.background = 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)';
            } else {
                scoreDisplay.style.background = 'linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%)';
            }
        }
        
        function resetSubtopic(button) {
            const subtopicItem = button.closest('.subtopic-item');
            const slider = subtopicItem.querySelector('.slider');
            const scoreDisplay = subtopicItem.querySelector('.score-display');
            
            slider.value = 0;
            scoreDisplay.textContent = 'Not assessed';
            scoreDisplay.style.background = 'linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%)';
            button.style.display = 'none';
        }
        
        // Initialize colors on page load
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('.slider').forEach(slider => {
                const scoreId = 'score_' + slider.name.replace('subtopic_', '');
                updateScore(slider, scoreId);
            });
        });
        </script>
    </body>
    </html>
    """
    
    db.close()
    return html

@app.route('/save-session/<int:student_id>', methods=['POST'])
def save_session(student_id):
    """Save session progress data"""
    db = get_db()
    
    # Process form data
    updates_made = []
    
    for field_name, value in request.form.items():
        if field_name.startswith('subtopic_'):
            subtopic_id = int(field_name.replace('subtopic_', ''))
            mastery_level = int(value)
            
            if mastery_level > 0:  # Only update if level is set
                db.update_subtopic_progress(
                    student_id, subtopic_id, mastery_level,
                    notes="Web session entry"
                )
                updates_made.append(f"Updated subtopic {subtopic_id} to level {mastery_level}")
    
    # Get student name for success message
    students = db.get_all_students()
    student_name = "Student"
    for s in students:
        if s[0] == student_id:
            student_name = s[1]
            break
    
    html = f"""
    <h1>✅ Session Saved Successfully!</h1>
    <p><strong>Student:</strong> {student_name}</p>
    <p><strong>Updates:</strong> {len(updates_made)} subtopics updated</p>
    
    <div style="margin: 20px 0;">
        <p><a href="/student/{student_id}">📊 View {student_name}'s Progress</a></p>
        <p><a href="/session/{student_id}">⚡ Enter Another Session</a></p>
        <p><a href="/students">📚 All Students</a></p>
        <p><a href="/">🏠 Home</a></p>
    </div>
    """
    
    db.close()
    return html

@app.route('/add-student')
def add_student_form():
    """Show form to add a new student"""
    html = """
    <h1>➕ Add New Student</h1>
    <form method="POST" action="/save-student">
        <div style="margin: 20px 0; max-width: 500px;">
            <div style="margin: 15px 0;">
                <label style="display: block; margin-bottom: 5px;"><strong>Student Name:</strong></label>
                <input type="text" name="name" required style="width: 100%; padding: 8px; font-size: 16px;">
            </div>
            
            <div style="margin: 15px 0;">
                <label style="display: block; margin-bottom: 5px;"><strong>Age:</strong></label>
                <input type="number" name="age" min="4" max="18" required style="width: 100%; padding: 8px; font-size: 16px;">
            </div>
            
            <div style="margin: 15px 0;">
                <label style="display: block; margin-bottom: 5px;"><strong>Year Group:</strong></label>
                <select name="year_group" required style="width: 100%; padding: 8px; font-size: 16px;">
                    <option value="">Select year group...</option>
                    <option value="Year 3">Year 3</option>
                    <option value="Year 4">Year 4</option>
                    <option value="Year 5">Year 5</option>
                    <option value="Year 6">Year 6</option>
                </select>
            </div>
            
            <div style="margin: 15px 0;">
                <label style="display: block; margin-bottom: 5px;"><strong>Target School (optional):</strong></label>
                <input type="text" name="target_school" style="width: 100%; padding: 8px; font-size: 16px;">
            </div>
            
            <div style="margin: 15px 0;">
                <label style="display: block; margin-bottom: 5px;"><strong>Parent Contact (optional):</strong></label>
                <input type="text" name="parent_contact" style="width: 100%; padding: 8px; font-size: 16px;">
            </div>
            
            <div style="margin: 15px 0;">
                <label style="display: block; margin-bottom: 5px;"><strong>Notes (optional):</strong></label>
                <textarea name="notes" rows="3" style="width: 100%; padding: 8px; font-size: 16px;"></textarea>
            </div>
            
            <button type="submit" style="background: #4CAF50; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 16px; margin-top: 10px;">
                ➕ Add Student
            </button>
        </div>
    </form>
    
    <hr>
    <p><a href="/students">📚 All Students</a> | <a href="/">🏠 Home</a></p>
    """
    return html

@app.route('/save-student', methods=['POST'])
def save_student():
    """Save new student to database"""
    db = get_db()
    
    # Get form data
    name = request.form.get('name', '').strip()
    age = request.form.get('age')
    year_group = request.form.get('year_group', '').strip()
    target_school = request.form.get('target_school', '').strip() or None
    parent_contact = request.form.get('parent_contact', '').strip() or None
    notes = request.form.get('notes', '').strip() or None
    
    # Validate required fields
    if not name:
        db.close()
        return "<h1>❌ Error</h1><p>Student name is required!</p><p><a href='/add-student'>Try again</a></p>"
    
    if not age or not age.isdigit():
        db.close()
        return "<h1>❌ Error</h1><p>Valid age is required!</p><p><a href='/add-student'>Try again</a></p>"
    
    if not year_group:
        db.close()
        return "<h1>❌ Error</h1><p>Year group is required!</p><p><a href='/add-student'>Try again</a></p>"
    
    # Add student to database
    student_id = db.add_student(name, int(age), year_group, target_school, parent_contact, notes)
    
    if student_id:
        html = f"""
        <h1>✅ Student Added Successfully!</h1>
        <div style="border: 1px solid #4CAF50; padding: 20px; margin: 20px 0; border-radius: 8px; background: #f0f8f0;">
            <h3>🎓 {name}</h3>
            <p><strong>Age:</strong> {age}</p>
            <p><strong>Year Group:</strong> {year_group}</p>
            {f'<p><strong>Target School:</strong> {target_school}</p>' if target_school else ''}
            {f'<p><strong>Parent Contact:</strong> {parent_contact}</p>' if parent_contact else ''}
            {f'<p><strong>Notes:</strong> {notes}</p>' if notes else ''}
        </div>
        
        <div style="margin: 20px 0;">
            <p><a href="/student/{student_id}">📊 View {name}'s Progress</a></p>
            <p><a href="/session/{student_id}">⚡ Start First Assessment</a></p>
            <p><a href="/add-student">➕ Add Another Student</a></p>
            <p><a href="/students">📚 All Students</a></p>
            <p><a href="/">🏠 Home</a></p>
        </div>
        """
    else:
        html = """
        <h1>❌ Error Adding Student</h1>
        <p>There was a problem adding the student to the database.</p>
        <p><a href="/add-student">Try again</a></p>
        """
    
    db.close()
    return html



if __name__ == '__main__':
    print("🚀 Starting Tutor AI Flask App...")
    print("📱 Access from other devices on your network:")
    print("   Find your IP address and use: http://YOUR_IP:5001")
    print("🌐 Local access: http://localhost:5001")
    print("⚠️  Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5001)