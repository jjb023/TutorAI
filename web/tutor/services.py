from utils.db_connection import get_db
from werkzeug.security import generate_password_hash

class TutorService:
    @staticmethod
    def get_all_tutors():
        """Get all tutors using your existing database structure."""
        with get_db() as conn:
            # Get all active tutors
            result = conn.execute('SELECT * FROM tutors WHERE active = true ORDER BY full_name')
            return result.fetchall()
    
    @staticmethod
    def get_tutor(tutor_id):
        """Get a tutor by ID."""
        with get_db() as conn:
            result = conn.execute('SELECT * FROM tutors WHERE id = ?', (tutor_id,))
            return result.fetchone()
    
    @staticmethod
    def create_tutor(username, full_name, email=None, password=None, role='tutor'):
        """Create a new tutor with proper password hashing and role."""
        # If no password provided, use a default temporary password
        if not password:
            password = f"{username}123"  # Default pattern: username + 123
        
        # Hash the password
        password_hash = generate_password_hash(password)
        
        with get_db() as conn:
            conn.execute(
                'INSERT INTO tutors (username, password_hash, full_name, email, role, active) VALUES (?, ?, ?, ?, ?, ?)',
                (username, password_hash, full_name, email, role, True)
            )
            
        return password  # Return the password so admin knows what it is
    
    @staticmethod
    def update_tutor(tutor_id, username, full_name, email=None, role=None):
        """Update a tutor."""
        with get_db() as conn:
            if role:
                conn.execute(
                    'UPDATE tutors SET username = ?, full_name = ?, email = ?, role = ? WHERE id = ?',
                    (username, full_name, email, role, tutor_id)
                )
            else:
                conn.execute(
                    'UPDATE tutors SET username = ?, full_name = ?, email = ? WHERE id = ?',
                    (username, full_name, email, tutor_id)
                )
    
    @staticmethod
    def update_tutor_password(tutor_id, new_password):
        """Update a tutor's password with proper hashing."""
        password_hash = generate_password_hash(new_password)
        
        with get_db() as conn:
            conn.execute(
                'UPDATE tutors SET password_hash = ? WHERE id = ?',
                (password_hash, tutor_id)
            )
    
    @staticmethod
    def reset_tutor_password(tutor_id, username):
        """Reset a tutor's password to default and return the new password."""
        new_password = f"{username}123"
        password_hash = generate_password_hash(new_password)
        
        with get_db() as conn:
            conn.execute(
                'UPDATE tutors SET password_hash = ? WHERE id = ?',
                (password_hash, tutor_id)
            )
            
        return new_password
    
    @staticmethod
    def delete_tutor(tutor_id):
        """Delete a tutor (set inactive)."""
        with get_db() as conn:
            conn.execute('UPDATE tutors SET active = false WHERE id = ?', (tutor_id,))
    
    @staticmethod
    def get_tutor_sessions(tutor_id):
        """Get all sessions for a tutor."""
        with get_db() as conn:
            result = conn.execute('''
                SELECT s.*, st.name as student_name 
                FROM sessions s
                JOIN students st ON s.student_id = st.id
                WHERE s.tutor_id = ?
                ORDER BY s.session_date DESC
            ''', (tutor_id,))
            return result.fetchall()
    
    @staticmethod
    def get_tutors_by_role(role):
        """Get all tutors with a specific role."""
        with get_db() as conn:
            result = conn.execute(
                'SELECT * FROM tutors WHERE role = ? AND active = true ORDER BY full_name',
                (role,)
            )
            return result.fetchall()
    
    @staticmethod
    def get_admins():
        """Get all admin users."""
        return TutorService.get_tutors_by_role('admin')
    
    @staticmethod
    def get_regular_tutors():
        """Get all regular tutor users."""
        return TutorService.get_tutors_by_role('tutor')
    
    @staticmethod
    def is_admin(tutor_id):
        """Check if a tutor has admin role."""
        with get_db() as conn:
            result = conn.execute(
                'SELECT role FROM tutors WHERE id = ? AND active = true',
                (tutor_id,)
            ).fetchone()
            
            if result:
                if isinstance(result, dict):
                    return result['role'] == 'admin'
                else:
                    return result[0] == 'admin'
            return False
    
    @staticmethod
    def update_tutor_status(tutor_id, active_status):
        """Update tutor active status (admin only function)."""
        with get_db() as conn:
            conn.execute(
                'UPDATE tutors SET active = ? WHERE id = ?',
                (active_status, tutor_id)
            )