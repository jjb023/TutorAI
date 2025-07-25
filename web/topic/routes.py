# web/topic/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .services import TopicService

topic_bp = Blueprint('topic', __name__, url_prefix='/topics')

@topic_bp.route('/')
@login_required
def list_topics():
    """Show all main topics with or without management options."""
    view_only = request.args.get('view_only', 'false').lower() == 'true'
    
    topics = TopicService.get_all_main_topics()
    return render_template('topic/list.html', topics=topics, view_only=view_only)

@topic_bp.route('/<int:topic_id>')
@login_required
def topic_detail(topic_id):
    """Show topic details with subtopics."""
    topic = TopicService.get_main_topic(topic_id)
    if not topic:
        flash('Topic not found!', 'error')
        return redirect(url_for('topic.list_topics'))
    
    subtopics = TopicService.get_subtopics_by_main_topic(topic_id)
    return render_template('topic/detail.html', topic=topic, subtopics=subtopics)

@topic_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_topic():
    """Add a new main topic (admin only)."""
    if current_user.username != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('topic.list_topics'))
    
    if request.method == 'POST':
        topic_name = request.form.get('topic_name', '').strip()
        description = request.form.get('description', '').strip() or None
        target_year_groups = request.form.get('target_year_groups', '').strip() or None
        color_code = request.form.get('color_code', '').strip() or '#607EBC'
        
        if not topic_name:
            flash('Topic name is required!', 'error')
            return render_template('topic/edit.html')
        
        try:
            TopicService.create_main_topic(topic_name, description, target_year_groups, color_code)
            flash(f'Topic {topic_name} added successfully!', 'success')
            return redirect(url_for('topic.list_topics'))
        except Exception as e:
            flash(f'Error adding topic: {e}', 'error')
    
    return render_template('topic/edit.html')

@topic_bp.route('/<int:topic_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_topic(topic_id):
    """Edit topic details (admin only)."""
    if current_user.username != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('topic.list_topics'))
    
    topic = TopicService.get_main_topic(topic_id)
    if not topic:
        flash('Topic not found!', 'error')
        return redirect(url_for('topic.list_topics'))
    
    if request.method == 'POST':
        topic_name = request.form.get('topic_name', '').strip()
        description = request.form.get('description', '').strip() or None
        target_year_groups = request.form.get('target_year_groups', '').strip() or None
        color_code = request.form.get('color_code', '').strip() or topic.color_code
        
        if not topic_name:
            flash('Topic name is required!', 'error')
            return render_template('topic/edit.html', topic=topic)
        
        try:
            TopicService.update_main_topic(topic_id, topic_name, description, target_year_groups, color_code)
            flash(f'Topic {topic_name} updated successfully!', 'success')
            return redirect(url_for('topic.topic_detail', topic_id=topic_id))
        except Exception as e:
            flash(f'Error updating topic: {e}', 'error')
    
    return render_template('topic/edit.html', topic=topic)

@topic_bp.route('/<int:topic_id>/delete', methods=['POST'])
@login_required
def delete_topic(topic_id):
    """Delete topic (admin only)."""
    if current_user.username != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('topic.list_topics'))
    
    try:
        TopicService.delete_main_topic(topic_id)
        flash('Topic deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting topic: {e}', 'error')
    
    return redirect(url_for('topic.list_topics'))

@topic_bp.route('/<int:topic_id>/add-subtopic', methods=['GET', 'POST'])
@login_required
def add_subtopic(topic_id):
    """Add a subtopic to a main topic (admin only)."""
    if current_user.username != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('topic.topic_detail', topic_id=topic_id))
    
    topic = TopicService.get_main_topic(topic_id)
    if not topic:
        flash('Topic not found!', 'error')
        return redirect(url_for('topic.list_topics'))
    
    if request.method == 'POST':
        subtopic_name = request.form.get('subtopic_name', '').strip()
        description = request.form.get('description', '').strip() or None
        difficulty_order = request.form.get('difficulty_order', type=int) or 1
        
        if not subtopic_name:
            flash('Subtopic name is required!', 'error')
            return render_template('topic/subtopic_edit.html', topic=topic)
        
        try:
            TopicService.create_subtopic(topic_id, subtopic_name, description, difficulty_order)
            flash(f'Subtopic {subtopic_name} added successfully!', 'success')
            return redirect(url_for('topic.topic_detail', topic_id=topic_id))
        except Exception as e:
            flash(f'Error adding subtopic: {e}', 'error')
    
    return render_template('topic/subtopic_edit.html', topic=topic)

@topic_bp.route('/<int:topic_id>/subtopic/<int:subtopic_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_subtopic(topic_id, subtopic_id):
    """Edit a subtopic (admin only)."""
    if current_user.username != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('topic.topic_detail', topic_id=topic_id))
    
    topic = TopicService.get_main_topic(topic_id)
    subtopic = TopicService.get_subtopic(subtopic_id)
    
    if not topic or not subtopic:
        flash('Topic or subtopic not found!', 'error')
        return redirect(url_for('topic.list_topics'))
    
    if request.method == 'POST':
        subtopic_name = request.form.get('subtopic_name', '').strip()
        description = request.form.get('description', '').strip() or None
        difficulty_order = request.form.get('difficulty_order', type=int) or 1
        
        if not subtopic_name:
            flash('Subtopic name is required!', 'error')
            return render_template('topic/subtopic_edit.html', topic=topic, subtopic=subtopic)
        
        try:
            TopicService.update_subtopic(subtopic_id, subtopic_name, description, difficulty_order)
            flash(f'Subtopic {subtopic_name} updated successfully!', 'success')
            return redirect(url_for('topic.topic_detail', topic_id=topic_id))
        except Exception as e:
            flash(f'Error updating subtopic: {e}', 'error')
    
    return render_template('topic/subtopic_edit.html', topic=topic, subtopic=subtopic)

@topic_bp.route('/<int:topic_id>/subtopic/<int:subtopic_id>/delete', methods=['POST'])
@login_required
def delete_subtopic(topic_id, subtopic_id):
    """Delete a subtopic (admin only)."""
    if current_user.username != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('topic.topic_detail', topic_id=topic_id))
    
    try:
        TopicService.delete_subtopic(subtopic_id)
        flash('Subtopic deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting subtopic: {e}', 'error')
    
    return redirect(url_for('topic.topic_detail', topic_id=topic_id))