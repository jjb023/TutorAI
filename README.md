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

| Tool         | Purpose                          |
|--------------|----------------------------------|
| Python       | Core logic and AI integration    |
| SQLite       | Lightweight local database       |
| VSCode       | Development environment          |
| OpenAI API   | Worksheet and question generation |
| GitHub       | Version control                  |
| Streamlit or Flask (optional) | Frontend/UI     |

---

## Roadmap – Steps to Complete

### Phase 1: Planning & Setup
- [x] Define goal, user (tutors), and data structure
- [x] Set up GitHub repo and folder structure
- [x] Create README

### Phase 2: Database + Logic
- [ ] Set up SQLite schema for Students, Sessions, Topics
- [ ] Build Python functions to insert/query session data
- [ ] Create logic to update topic performance based on results

### Phase 3: Worksheet Generator
- [ ] Create prompt templates for OpenAI API
- [ ] Build function to generate 5–10 practice questions on weak topics
- [ ] Store generated worksheets by student and topic

### Phase 4: Dashboard / UI (Optional)
- [ ] Build command-line or Streamlit interface to:
  - Add/view students
  - View strengths/weaknesses
  - Generate and download worksheet

### Phase 5: Testing & Polish
- [ ] Test full loop: log → analyse → generate worksheet
- [ ] Add sample student data
- [ ] Write usage instructions in README

### Phase 6: Future Features (Backlog)
- [ ] Export printable PDFs of worksheets
- [ ] Add tagging by year group or curriculum level
- [ ] Support English/literacy questions
- [ ] Allow bulk upload of student info
- [ ] Deploy web version (Flask + SQLite or Firebase)

---

## How to Run the Project

```bash
git clone https://github.com/yourusername/tutor-ai.git
cd tutor-ai

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
python main.py

```

---

## Time Log

| Date | Time Spent (Hours) | Tasks Completed |
|------|------------|-----------------|
| 23.05.25 | 1.5 | Set up github repo and folder structure, created readme |
| 27.05.25|  |  |









