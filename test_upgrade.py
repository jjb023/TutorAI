from database import TutorAIDatabase

# Create database instance
db = TutorAIDatabase()

# Run the upgrade
db.upgrade_for_multitutor()

# Check it worked
tutors = db.get_all_tutors()
print("Tutors:", tutors)

db.close()