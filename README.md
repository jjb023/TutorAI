# TutorAI

# Tutor AI – Personalised Progress Tracker for Tutors

A lightweight tool built for private tutors to track student progress in 7+ UK school-level Maths, identify topic strengths/weaknesses, and automatically generate personalised worksheets for upcoming sessions using AI.

---

## Project Purpose

Many tutors lack a structured system to:
- Track student performance over time
- Identify trends in topic mastery
- Know what to focus on in the next session

**Tutor AI** solves this by acting as a central, intelligent database that logs sessions, monitors topic performance, and uses AI to create tailored practice material.

---

## Project Outcome

- A simple UI where tutors can:
  - Log students and sessions
  - View topic-level trends per student
  - Instantly generate custom worksheets using GPT
- A local SQLite database to persist student data
- A scalable Python backend that could later be deployed or extended into a web app

---

## Tech Stack

| Tool         | Purpose                          | Status |
|--------------|----------------------------------|--------|
| Python       | Core logic and AI integration    | Active |
| SQLite       | Lightweight local database       | Active |
| VSCode       | Development environment          | Active |
| OpenAI API   | Worksheet and question generation | Planned |
| GitHub       | Version control                  | Active |
| Flask        | Frontend/UI                      | Active |

---

## Roadmap – Steps to Complete

### Phase 1: Planning & Setup 
- [x] Define goal, user (tutors), and data structure
- [x] Set up GitHub repo and folder structure
- [x] Create README with comprehensive roadmap
- [x] Hierarchical topic structure (main topics → subtopics)
- [x] 1-10 mastery scale implementation
- [x] SQLite database schema design

### Phase 2: Core Database & CLI 
- [x] Set up SQLite schema for Students, Sessions, Topics
- [x] Build Python functions to insert/query session data
- [x] Logic to update topic performance tracking
- [x] Progress tracking with completion percentages
- [x] Working CLI interface with session entry
- [x] Subtopic search functionality
- [x] Multi-tutor authentication system
- [x] Database migration tools for upgrades

### Phase 3: Web Interface MVP 
- [x] Flask app setup with modular blueprint structure
- [x] Professional dashboard with statistics overview
- [x] Mobile-optimized session entry form with touch-friendly sliders
- [x] Complete student management (add/edit/delete/view progress)
- [x] Comprehensive progress visualization with color-coded indicators
- [x] Multi-tutor concurrent access with role-based permissions
- [x] Modern, responsive design with customizable CSS themes
- [x] Cross-device compatibility (desktop, tablet, mobile)
- [x] Secure tutor login system with Flask-Login
- [x] Topic and subtopic management interface
- [x] Detailed student progress reports with mastery tracking
- [x] Session logging with subtopic assessment integration

### Phase 4: Code Architecture & Polish 
- [x] Modular Flask blueprint structure (/auth, /student, /tutor, /session, /topic)
- [x] Service layer separation for business logic
- [x] Database utilities and connection management
- [x] Comprehensive error handling and flash messaging
- [ ] **Code documentation and inline comments**
- [ ] **Unit tests for core functionality**
- [ ] **Configuration management (dev/prod environments)**
- [ ] **Data validation and input sanitization**
- [ ] **Performance optimization and query efficiency**

### Phase 5: Worksheet Generator & AI Integration
- [ ] Question bank database structure with categorization
- [ ] Basic question templates by subtopic and difficulty level
- [ ] Smart worksheet generation algorithm focusing on weak areas
- [ ] PDF generation for printable worksheets with proper formatting
- [ ] Worksheet tracking system (generated → assigned → completed)
- [ ] OpenAI API integration for dynamic question creation
- [ ] Worksheet library and template management
- [ ] Student worksheet history and performance tracking
- [ ] Custom worksheet difficulty adjustment based on mastery levels

### Phase 6: Deployment & Production
- [ ] Environment configuration for production deployment
- [ ] Deploy to cloud platform (Railway/Render/Heroku/DigitalOcean)
- [ ] Custom domain setup and SSL certificate
- [ ] Database backup and recovery procedures
- [ ] Performance monitoring and logging
- [ ] User acceptance testing with real tutors
- [ ] Comprehensive user documentation and tutorials
- [ ] Security audit and penetration testing

### Phase 7: Advanced Features
- [ ] **Analytics Dashboard**
  - [ ] Student progress trends over time
  - [ ] Topic difficulty analysis across students
  - [ ] Tutor performance metrics and insights
  - [ ] Predictive modeling for student outcomes
- [ ] **Parent Portal**
  - [ ] Progress reports (PDF export)
  - [ ] Parent login system with limited access
  - [ ] Email notifications for milestones
  - [ ] Homework and assignment tracking
- [ ] **Enhanced Assessment**
  - [ ] Worksheet scanning & auto-grading capability
  - [ ] Voice note recording for session observations
  - [ ] Photo upload for written work samples
  - [ ] Custom assessment rubrics by topic

### Phase 8: Platform Expansion
- [ ] **Multi-Subject Support**
  - [ ] English/Literacy curriculum integration
  - [ ] Science topics and practical assessments
  - [ ] Language learning modules
  - [ ] Custom subject creation tools
- [ ] **Advanced Integrations**
  - [ ] Integration with popular tutoring management systems
  - [ ] Calendar integration for session scheduling
  - [ ] Payment processing for online tutoring
  - [ ] Video conferencing integration
- [ ] **Mobile Application**
  - [ ] Native iOS/Android app development
  - [ ] Offline mode for session entry
  - [ ] Push notifications for assignments
  - [ ] Camera integration for worksheet scanning



---

## Current Project Structure

tutor_ai_project/

.
├── __pycache__
│   └── database.cpython-311.pyc
├── data
│   └── tutor_ai.db
├── database.py
├── README.md
├── test_upgrade.py
├── tutor_ai.py
└── web
    ├── app.py
    ├── static
    │   └── style.css
    └── templates

Current dependencies: Flask

---

## How to Run the Project

```bash

cd web
python app.py

```

---

## Time Log

| Date | Time Spent (Hours) | Tasks Completed |
|------|------------|-----------------|
| 23.05.25 | *1.5* | Set up github repo and folder structure, created readme |
| 27.05.25 | *3.5* | Created data base with dummy names, created access to data base |
| 28.05.25 | *4* | Code changes, readme changes, roadmap updates|
| 29.05.25 | *6* | Local flask website successfully launched |
| 02.06.25 | *3.5* | Added log in abilities for tutors |
| 03.06.25 | 1.5 | File Restructure |
| 17.06.25 | 2 | Topics + subtopic integration |
| 27.06.25 | 1.5 | Migrating databases + adding worksheets |
| 08.07.25 | 1.5 | System Health checks and worksheet prep | 
| 14.07.25 | 4 | Worksheet generation + subtopic question bank implementation |
| 16.07.25 | 2 | Question population and worksheet |
















