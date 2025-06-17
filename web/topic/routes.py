from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .services import TopicService

topic_bp = Blueprint('topic', __name__, url_prefix='/topics')

@topic_bp.route('/')
@login_required
def list_topics():
    """Show all main topics."""
    topics = TopicService.get_all_main_topics()
    return render_template('topic/list.html', topics=topics)

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