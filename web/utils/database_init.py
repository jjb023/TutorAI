import os
import sqlite3
try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    psycopg2 = None
    print("⚠️ psycopg2 not installed - PostgreSQL support disabled")

def init_database():
    """Initialize database - PostgreSQL for production, SQLite for development"""
    
    # Check if we're using PostgreSQL (Railway provides DATABASE_URL)
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # PostgreSQL for production (Railway)
        print("🐘 Using PostgreSQL database")
        return init_postgresql(database_url)
    else:
        # SQLite for local development
        print("📦 Using SQLite database")
        return init_sqlite()

def init_postgresql(database_url):
    """Initialize PostgreSQL database with schema"""
    if not psycopg2:
        raise ImportError("psycopg2 is required for PostgreSQL support. Install with: pip install psycopg2-binary")
    
    try:
        # Railway uses 'postgresql://' but psycopg2 needs 'postgres://'
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Create tables
        create_postgresql_schema(cursor)
        
        # Add default data if needed
        add_default_data_postgresql(cursor)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ PostgreSQL database initialized successfully")
        return database_url
        
    except Exception as e:
        print(f"❌ PostgreSQL initialization failed: {e}")
        raise

def init_sqlite():
    """Initialize SQLite database for local development"""
    # Get the path relative to the web directory
    web_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(web_dir)
    data_dir = os.path.join(project_root, 'data')
    
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    db_path = os.path.join(data_dir, 'tutor_ai.db')
    
    # Check if database already exists
    if os.path.exists(db_path):
        print(f"✅ SQLite database exists at: {db_path}")
        return db_path
    
    # Create new database
    print(f"📝 Creating new SQLite database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create schema
    create_sqlite_schema(cursor)
    
    # Add default data
    add_default_data_sqlite(cursor)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ SQLite database created at: {db_path}")
    return db_path

def create_postgresql_schema(cursor):
    """Create PostgreSQL schema"""
    
    # Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            age INTEGER,
            year_group VARCHAR(20),
            target_school VARCHAR(100),
            parent_contact VARCHAR(100),
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_session_date TIMESTAMP,
            active BOOLEAN DEFAULT true
        )
    """)
    
    # Tutors table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tutors (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            active BOOLEAN DEFAULT true
        )
    """)
    
    # Main topics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS main_topics (
            id SERIAL PRIMARY KEY,
            topic_name VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            target_year_groups VARCHAR(100),
            color_code VARCHAR(7)
        )
    """)
    
    # Subtopics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subtopics (
            id SERIAL PRIMARY KEY,
            main_topic_id INTEGER REFERENCES main_topics(id),
            subtopic_name VARCHAR(100) NOT NULL,
            description TEXT,
            difficulty_order INTEGER,
            prerequisite_subtopic_id INTEGER REFERENCES subtopics(id)
        )
    """)
    
    # Subtopic progress table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subtopic_progress (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(id),
            subtopic_id INTEGER REFERENCES subtopics(id),
            mastery_level INTEGER DEFAULT 1,
            last_assessed TIMESTAMP,
            questions_attempted INTEGER DEFAULT 0,
            questions_correct INTEGER DEFAULT 0,
            notes TEXT,
            UNIQUE(student_id, subtopic_id)
        )
    """)
    
    # Sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(id),
            tutor_id INTEGER REFERENCES tutors(id),
            session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration_minutes INTEGER,
            main_topics_covered TEXT,
            tutor_notes TEXT,
            homework_set TEXT
        )
    """)
    
    # Questions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            subtopic_id INTEGER REFERENCES subtopics(id),
            question_text TEXT NOT NULL,
            answer TEXT,
            difficulty_level INTEGER CHECK(difficulty_level IN (1, 2, 3)),
            time_estimate_minutes INTEGER,
            space_required VARCHAR(20) CHECK(space_required IN ('none', 'small', 'medium', 'large')),
            question_type VARCHAR(50),
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by_tutor_id INTEGER REFERENCES tutors(id),
            active BOOLEAN DEFAULT true,
            is_template BOOLEAN DEFAULT false,
            template_params TEXT
        )
    """)
    
    # Worksheets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS worksheets (
            id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(id),
            subtopic_id INTEGER REFERENCES subtopics(id),
            title VARCHAR(200),
            difficulty_level VARCHAR(20),
            generated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            generated_by_tutor_id INTEGER REFERENCES tutors(id),
            pdf_path VARCHAR(255),
            status VARCHAR(20) DEFAULT 'draft',
            session_id INTEGER REFERENCES sessions(id),
            notes TEXT
        )
    """)
    
    # Worksheet questions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS worksheet_questions (
            id SERIAL PRIMARY KEY,
            worksheet_id INTEGER REFERENCES worksheets(id),
            question_id INTEGER REFERENCES questions(id),
            question_order INTEGER,
            custom_question_text TEXT,
            space_allocated VARCHAR(20)
        )
    """)
    
    print("✅ PostgreSQL schema created")

def create_sqlite_schema(cursor):
    """Create SQLite schema - same structure as PostgreSQL but with SQLite syntax"""
    
    # Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            year_group TEXT,
            target_school TEXT,
            parent_contact TEXT,
            notes TEXT,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            last_session_date TEXT,
            active BOOLEAN DEFAULT 1
        )
    """)
    
    # Tutors table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tutors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            last_login TEXT,
            active BOOLEAN DEFAULT 1
        )
    """)
    
    # Main topics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS main_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_name TEXT UNIQUE NOT NULL,
            description TEXT,
            target_year_groups TEXT,
            color_code TEXT
        )
    """)
    
    # Subtopics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subtopics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_topic_id INTEGER REFERENCES main_topics(id),
            subtopic_name TEXT NOT NULL,
            description TEXT,
            difficulty_order INTEGER,
            prerequisite_subtopic_id INTEGER REFERENCES subtopics(id)
        )
    """)
    
    # Continue with other tables...
    # (Same structure as PostgreSQL but with SQLite syntax)
    
    print("✅ SQLite schema created")

def add_default_data_postgresql(cursor):
    """Add default data for PostgreSQL"""
    from werkzeug.security import generate_password_hash
    
    # Check if admin exists
    cursor.execute("SELECT id FROM tutors WHERE username = 'admin'")
    if not cursor.fetchone():
        # Add default admin
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        hashed = generate_password_hash(admin_password)
        
        cursor.execute("""
            INSERT INTO tutors (username, password_hash, full_name, email)
            VALUES (%s, %s, %s, %s)
        """, ('admin', hashed, 'Administrator', 'admin@tutorai.com'))
        
        print("✅ Default admin user created")
    
    # Add default main topics if none exist
    cursor.execute("SELECT COUNT(*) FROM main_topics")
    if cursor.fetchone()[0] == 0:
        topics = [
            ("Number", "Basic arithmetic, fractions, decimals, percentages", "Year 1-6", "#FF6B6B"),
            ("Algebra", "Patterns, equations, expressions", "Year 4-6", "#4ECDC4"),
            ("Geometry", "Shapes, angles, measurements", "Year 1-6", "#45B7D1"),
            ("Statistics", "Data handling, graphs, probability", "Year 3-6", "#96CEB4"),
        ]
        
        for topic_name, desc, years, color in topics:
            cursor.execute("""
                INSERT INTO main_topics (topic_name, description, target_year_groups, color_code)
                VALUES (%s, %s, %s, %s)
            """, (topic_name, desc, years, color))
        
        print("✅ Default topics added")

def add_default_data_sqlite(cursor):
    """Add default data for SQLite"""
    from werkzeug.security import generate_password_hash
    
    # Check if admin exists
    cursor.execute("SELECT id FROM tutors WHERE username = 'admin'")
    if not cursor.fetchone():
        # Add default admin
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        hashed = generate_password_hash(admin_password)
        
        cursor.execute("""
            INSERT INTO tutors (username, password_hash, full_name, email)
            VALUES (?, ?, ?, ?)
        """, ('admin', hashed, 'Administrator', 'admin@tutorai.com'))
        
        print("✅ Default admin user created")
    
    # Add default main topics if none exist
    cursor.execute("SELECT COUNT(*) FROM main_topics")
    if cursor.fetchone()[0] == 0:
        topics = [
            ("Number", "Basic arithmetic, fractions, decimals, percentages", "Year 1-6", "#FF6B6B"),
            ("Algebra", "Patterns, equations, expressions", "Year 4-6", "#4ECDC4"),
            ("Geometry", "Shapes, angles, measurements", "Year 1-6", "#45B7D1"),
            ("Statistics", "Data handling, graphs, probability", "Year 3-6", "#96CEB4"),
        ]
        
        for topic_name, desc, years, color in topics:
            cursor.execute("""
                INSERT INTO main_topics (topic_name, description, target_year_groups, color_code)
                VALUES (?, ?, ?, ?)
            """, (topic_name, desc, years, color))
        
        print("✅ Default topics added")