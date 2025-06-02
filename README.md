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

### Phase 1: Planning & Setup COMPLETE
- [x] Define goal, user (tutors), and data structure
- [x] Set up GitHub repo and folder structure
- [x] Create README
- [x] Hierarchical topic structure (main topics -> subtopics)
- [x] 1-10 mastery scale
 
### Phase 2: Database + Logic
- [x] Set up SQLite schema for Students, Sessions, Topics
- [x] Build Python functions to insert/query session data
- [x] Logic to update topiuc performance
- [x] Progress tracking with completion percentages
- [x] Working CLI interface with session entry
- [x] subtopic search functionality
- [x] Add multi tutor authentication tables

### Phase 3: Web interface (multi tutor mvp)
- [x] Flask app setup with static file serving
- [x] Professional dashboard showing all students
- [x] Mobile-optimized session entry form with touch-friendly sliders
- [x] Student management (add/edit/delete via web app)
- [x] Progress visualization with color-coded status indicators
- [x] Multi-tutor concurrent access capability
- [x] Modern, responsive design with customizable color themes
- [x] Cross-device compatibility (desktop, tablet, mobile)
- [ ] Optional: Simple tutor login system (5% remaining)

### Phase 4: Worksheet Generator
- [ ] Question bank database structure
- [ ] Basic question templates by subtopic and difficulty
- [ ] Smart worksheet generation focusing on weak areas
- [ ] PDF generation for printable worksheets
- [ ] Worksheet tracking (generated → printed → completed)
- [ ] Integration with OpenAI API for dynamic question creation
- [ ] Store generated worksheets by student and topic

### Phase 5: Testing & Polish
- [ ] Deploy to cloud platform (Render/Railway/Heroku)
- [ ] Custom domain setup
- [ ] Performance optimization for multiple concurrent users
- [ ] Enhanced error handling and data validation
- [ ] User acceptance testing with real tutors
- [ ] Documentation for tutors

### Phase 6: Future Features 
- [ ] Worksheet scanning & auto-grading capability
- [ ] Parent progress reports (PDF export)
- [ ] Additional subjects (English/Literacy)
- [ ] Advanced analytics and learning insights
- [ ] Native mobile app development
- [ ] Integration with popular tutoring management systems

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

python tutor_ai.py

```

---

## Time Log

| Date | Time Spent (Hours) | Tasks Completed |
|------|------------|-----------------|
| 23.05.25 | 1.5 | Set up github repo and folder structure, created readme |
| 27.05.25 | 3.5 | Created data base with dummy names, created access to data base |
| 28.05.25 | 4 | Code changes, readme changes, roadmap updates|
| 29.05.25 | 6 | Local flask website successfully launched |
| 02.06.25 | 3.5 | Added log in abilities for tutors |











