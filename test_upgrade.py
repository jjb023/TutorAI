from database import TutorAIDatabase

db = TutorAIDatabase("data/tutor_ai.db")

# Add demo tutors
demo_tutors = [
    ("admin", "password_hash", "Sarah Wilson", "sarah@tutorai.demo"),
    ("tutor1", "password_hash", "Mike Johnson", "mike@tutorai.demo"),
    ("tutor2", "password_hash", "Emma Davis", "emma@tutorai.demo")
]

for username, password, name, email in demo_tutors:
    db.add_tutor(username, password, name, email)

db.close()
print("Demo tutors added!")