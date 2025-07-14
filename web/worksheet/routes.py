from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from .services import WorksheetService, QuestionService
from student.services import StudentService
from topic.services import TopicService
import os

worksheet_bp = Blueprint('worksheet', __name__, url_prefix='/worksheets')

@worksheet_bp.route('/questions/<int:subtopic_id>')
@login_required
def question_bank(subtopic_id):
    """View and manage questions for a subtopic."""
    subtopic = TopicService.get_subtopic(subtopic_id)
    if not subtopic:
        flash('Subtopic not found!', 'error')
        return redirect(url_for('topic.list_topics'))
    
    questions = QuestionService.get_questions_by_subtopic(subtopic_id)
    stats = QuestionService.get_question_stats(subtopic_id)
    
    # Group questions by difficulty
    questions_by_difficulty = {
        'easy': [q for q in questions if q['difficulty_level'] == 1],
        'medium': [q for q in questions if q['difficulty_level'] == 2],
        'hard': [q for q in questions if q['difficulty_level'] == 3]
    }
    
    return render_template('worksheet/question_bank.html',
                         subtopic=subtopic,
                         questions_by_difficulty=questions_by_difficulty,
                         stats=stats)

@worksheet_bp.route('/questions/<int:subtopic_id>/add', methods=['GET', 'POST'])
@login_required
def add_question(subtopic_id):
    """Add a new question to the bank."""
    subtopic = TopicService.get_subtopic(subtopic_id)
    if not subtopic:
        flash('Subtopic not found!', 'error')
        return redirect(url_for('topic.list_topics'))
    
    if request.method == 'POST':
        question_text = request.form.get('question_text', '').strip()
        difficulty_level = request.form.get('difficulty_level', type=int)
        time_estimate = request.form.get('time_estimate', type=int)
        space_required = request.form.get('space_required')
        question_type = request.form.get('question_type', '').strip() or None
        
        if not question_text or not difficulty_level:
            flash('Question text and difficulty level are required!', 'error')
            return render_template('worksheet/question_edit.html', subtopic=subtopic)
        
        try:
            QuestionService.create_question(
                subtopic_id, question_text, difficulty_level,
                time_estimate, space_required, current_user.id, question_type
            )
            flash('Question added successfully!', 'success')
            return redirect(url_for('worksheet.question_bank', subtopic_id=subtopic_id))
        except Exception as e:
            flash(f'Error adding question: {e}', 'error')
    
    return render_template('worksheet/question_edit.html', subtopic=subtopic)

@worksheet_bp.route('/generate/<int:student_id>/<int:subtopic_id>')
@login_required
def generate_worksheet(student_id, subtopic_id):
    """Generate worksheet interface."""
    student = StudentService.get_student(student_id)
    subtopic = TopicService.get_subtopic(subtopic_id)
    
    if not student or not subtopic:
        flash('Invalid student or subtopic!', 'error')
        return redirect(url_for('student.list_students'))
    
    # Get recommendation
    recommended_level, recommended_dist = WorksheetService.get_recommended_difficulty(
        student_id, subtopic_id)
    
    # Get question stats
    stats = QuestionService.get_question_stats(subtopic_id)
    
    return render_template('worksheet/generate.html',
                         student=student,
                         subtopic=subtopic,
                         recommended_level=recommended_level,
                         recommended_dist=recommended_dist,
                         stats=stats)

@worksheet_bp.route('/generate', methods=['POST'])
@login_required
def create_worksheet():
    """Actually generate the worksheet."""
    student_id = request.form.get('student_id', type=int)
    subtopic_id = request.form.get('subtopic_id', type=int)
    
    # Get difficulty distribution
    easy_pct = request.form.get('easy_percentage', type=int) or 40
    medium_pct = request.form.get('medium_percentage', type=int) or 40
    hard_pct = request.form.get('hard_percentage', type=int) or 20
    
    # Ensure they add up to 100
    total = easy_pct + medium_pct + hard_pct
    if total != 100:
        # Normalize
        easy_pct = int(easy_pct * 100 / total)
        medium_pct = int(medium_pct * 100 / total)
        hard_pct = 100 - easy_pct - medium_pct
    
    difficulty_dist = {
        'easy': easy_pct,
        'medium': medium_pct,
        'hard': hard_pct
    }
    
    total_questions = request.form.get('total_questions', type=int) or 20
    title = request.form.get('title', '').strip() or None
    
    try:
        worksheet_id = WorksheetService.generate_worksheet(
            student_id, subtopic_id, current_user.id,
            difficulty_dist, total_questions, title
        )
        
        flash('Worksheet generated successfully!', 'success')
        return redirect(url_for('worksheet.edit_worksheet', worksheet_id=worksheet_id))
        
    except Exception as e:
        flash(f'Error generating worksheet: {e}', 'error')
        return redirect(url_for('worksheet.generate_worksheet', 
                              student_id=student_id, 
                              subtopic_id=subtopic_id))

@worksheet_bp.route('/<int:worksheet_id>/edit')
@login_required
def edit_worksheet(worksheet_id):
    """Edit worksheet before finalizing."""
    worksheet_data = WorksheetService.get_worksheet(worksheet_id)
    if not worksheet_data:
        flash('Worksheet not found!', 'error')
        return redirect(url_for('student.list_students'))
    
    return render_template('worksheet/edit.html',
                         worksheet=worksheet_data['worksheet'],
                         questions=worksheet_data['questions'])

@worksheet_bp.route('/<int:worksheet_id>/update', methods=['POST'])
@login_required
def update_worksheet(worksheet_id):
    """Update worksheet questions."""
    # Process each question update
    question_orders = request.form.getlist('question_order')
    
    for order in question_orders:
        new_text = request.form.get(f'question_text_{order}')
        new_space = request.form.get(f'space_{order}')
        
        if new_text:  # Only update if text was changed
            WorksheetService.update_worksheet_question(
                worksheet_id, int(order), new_text, new_space
            )
    
    flash('Worksheet updated!', 'success')
    return redirect(url_for('worksheet.edit_worksheet', worksheet_id=worksheet_id))

@worksheet_bp.route('/<int:worksheet_id>/finalize')
@login_required
def finalize_worksheet(worksheet_id):
    """Generate PDF and finalize worksheet."""
    from .pdf_generator import generate_worksheet_pdf
    
    worksheet_data = WorksheetService.get_worksheet(worksheet_id)
    if not worksheet_data:
        flash('Worksheet not found!', 'error')
        return redirect(url_for('student.list_students'))
    
    try:
        # Generate PDF
        pdf_path = generate_worksheet_pdf(worksheet_data)
        
        # Update worksheet status
        WorksheetService.finalize_worksheet(worksheet_id, pdf_path)
        
        flash('Worksheet finalized! PDF ready for download.', 'success')
        return redirect(url_for('worksheet.view_worksheet', worksheet_id=worksheet_id))
        
    except Exception as e:
        flash(f'Error generating PDF: {e}', 'error')
        return redirect(url_for('worksheet.edit_worksheet', worksheet_id=worksheet_id))

@worksheet_bp.route('/<int:worksheet_id>')
@login_required
def view_worksheet(worksheet_id):
    """View finalized worksheet."""
    worksheet_data = WorksheetService.get_worksheet(worksheet_id)
    if not worksheet_data:
        flash('Worksheet not found!', 'error')
        return redirect(url_for('student.list_students'))
    
    return render_template('worksheet/view.html',
                         worksheet=worksheet_data['worksheet'],
                         questions=worksheet_data['questions'])

@worksheet_bp.route('/<int:worksheet_id>/download')
@login_required
def download_worksheet(worksheet_id):
    """Download worksheet PDF."""
    worksheet_data = WorksheetService.get_worksheet(worksheet_id)
    if not worksheet_data or not worksheet_data['worksheet']['pdf_path']:
        flash('PDF not found!', 'error')
        return redirect(url_for('worksheet.view_worksheet', worksheet_id=worksheet_id))
    
    pdf_path = worksheet_data['worksheet']['pdf_path']
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True, 
                        download_name=f"worksheet_{worksheet_id}.pdf")
    else:
        flash('PDF file not found!', 'error')
        return redirect(url_for('worksheet.view_worksheet', worksheet_id=worksheet_id))