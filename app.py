from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database setup
DATABASE = 'nursing_app.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    
    # Create tables
    conn.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            course TEXT NOT NULL,
            due_date TEXT NOT NULL,
            weight INTEGER,
            status TEXT DEFAULT 'not-started',
            completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS clinical_shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            location TEXT NOT NULL,
            unit TEXT,
            hours REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS requirements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            deadline TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            renewal_months INTEGER DEFAULT 12,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            target_date TEXT NOT NULL,
            category TEXT DEFAULT 'academic',
            completed BOOLEAN DEFAULT 0,
            created_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course TEXT NOT NULL,
            assessment TEXT NOT NULL,
            type TEXT DEFAULT 'assignment',
            grade REAL NOT NULL,
            max_points REAL NOT NULL,
            weight REAL,
            date TEXT,
            percentage REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS stress_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            stress_level INTEGER NOT NULL,
            mood TEXT,
            notes TEXT,
            study_hours REAL,
            sleep_hours REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# API Routes

@app.route('/api/assignments', methods=['GET', 'POST'])
def assignments():
    conn = get_db_connection()
    
    if request.method == 'GET':
        assignments = conn.execute('SELECT * FROM assignments ORDER BY due_date ASC').fetchall()
        conn.close()
        return jsonify([dict(row) for row in assignments])
    
    elif request.method == 'POST':
        data = request.json
        conn.execute('''
            INSERT INTO assignments (title, course, due_date, weight, status, completed)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['title'], data['course'], data['dueDate'], 
              data.get('weight'), data.get('status', 'not-started'), 
              data.get('completed', False)))
        conn.commit()
        assignment_id = conn.lastrowid
        conn.close()
        return jsonify({'id': assignment_id}), 201

@app.route('/api/assignments/<int:assignment_id>', methods=['PUT', 'DELETE'])
def assignment_detail(assignment_id):
    conn = get_db_connection()
    
    if request.method == 'PUT':
        data = request.json
        conn.execute('''
            UPDATE assignments 
            SET title=?, course=?, due_date=?, weight=?, status=?, completed=?
            WHERE id=?
        ''', (data['title'], data['course'], data['dueDate'], 
              data.get('weight'), data.get('status'), 
              data.get('completed'), assignment_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        conn.execute('DELETE FROM assignments WHERE id = ?', (assignment_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

@app.route('/api/clinical-shifts', methods=['GET', 'POST'])
def clinical_shifts():
    conn = get_db_connection()
    
    if request.method == 'GET':
        shifts = conn.execute('SELECT * FROM clinical_shifts ORDER BY date ASC').fetchall()
        conn.close()
        return jsonify([dict(row) for row in shifts])
    
    elif request.method == 'POST':
        data = request.json
        conn.execute('''
            INSERT INTO clinical_shifts (date, start_time, end_time, location, unit, hours)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['date'], data.get('startTime'), data.get('endTime'),
              data['location'], data.get('unit'), data['hours']))
        conn.commit()
        shift_id = conn.lastrowid
        conn.close()
        return jsonify({'id': shift_id}), 201

@app.route('/api/clinical-shifts/<int:shift_id>', methods=['PUT', 'DELETE'])
def clinical_shift_detail(shift_id):
    conn = get_db_connection()
    
    if request.method == 'PUT':
        data = request.json
        conn.execute('''
            UPDATE clinical_shifts 
            SET date=?, start_time=?, end_time=?, location=?, unit=?, hours=?
            WHERE id=?
        ''', (data['date'], data.get('start_time'), data.get('end_time'),
              data['location'], data.get('unit'), data['hours'], shift_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        conn.execute('DELETE FROM clinical_shifts WHERE id = ?', (shift_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

@app.route('/api/requirements', methods=['GET', 'POST'])
def requirements():
    conn = get_db_connection()
    
    if request.method == 'GET':
        requirements = conn.execute('SELECT * FROM requirements ORDER BY deadline ASC').fetchall()
        conn.close()
        return jsonify([dict(row) for row in requirements])
    
    elif request.method == 'POST':
        data = request.json
        conn.execute('''
            INSERT INTO requirements (name, deadline, status, renewal_months)
            VALUES (?, ?, ?, ?)
        ''', (data['name'], data['deadline'], data.get('status', 'pending'),
              data.get('renewalMonths', 12)))
        conn.commit()
        req_id = conn.lastrowid
        conn.close()
        return jsonify({'id': req_id}), 201

@app.route('/api/requirements/<int:req_id>', methods=['PUT', 'DELETE'])
def requirement_detail(req_id):
    conn = get_db_connection()
    
    if request.method == 'PUT':
        data = request.json
        conn.execute('''
            UPDATE requirements 
            SET name=?, deadline=?, status=?, renewal_months=?
            WHERE id=?
        ''', (data['name'], data['deadline'], data['status'],
              data.get('renewalMonths', 12), req_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        conn.execute('DELETE FROM requirements WHERE id = ?', (req_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

@app.route('/api/goals', methods=['GET', 'POST'])
def goals():
    conn = get_db_connection()
    
    if request.method == 'GET':
        goals = conn.execute('SELECT * FROM goals ORDER BY target_date ASC').fetchall()
        conn.close()
        return jsonify([dict(row) for row in goals])
    
    elif request.method == 'POST':
        data = request.json
        conn.execute('''
            INSERT INTO goals (title, description, target_date, category, completed, created_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['title'], data.get('description'), data['targetDate'],
              data.get('category', 'academic'), data.get('completed', False),
              data.get('createdDate')))
        conn.commit()
        goal_id = conn.lastrowid
        conn.close()
        return jsonify({'id': goal_id}), 201

@app.route('/api/goals/<int:goal_id>', methods=['PUT', 'DELETE'])
def goal_detail(goal_id):
    conn = get_db_connection()
    
    if request.method == 'PUT':
        data = request.json
        conn.execute('''
            UPDATE goals 
            SET title=?, description=?, target_date=?, category=?, completed=?
            WHERE id=?
        ''', (data['title'], data.get('description'), data['targetDate'],
              data.get('category'), data.get('completed'), goal_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        conn.execute('DELETE FROM goals WHERE id = ?', (goal_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

@app.route('/api/grades', methods=['GET', 'POST'])
def grades():
    conn = get_db_connection()
    
    if request.method == 'GET':
        grades = conn.execute('SELECT * FROM grades ORDER BY date DESC').fetchall()
        conn.close()
        return jsonify([dict(row) for row in grades])
    
    elif request.method == 'POST':
        data = request.json
        percentage = round((float(data['grade']) / float(data['maxPoints'])) * 100)
        conn.execute('''
            INSERT INTO grades (course, assessment, type, grade, max_points, weight, date, percentage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['course'], data['assessment'], data.get('type', 'assignment'),
              data['grade'], data['maxPoints'], data.get('weight'),
              data.get('date'), percentage))
        conn.commit()
        grade_id = conn.lastrowid
        conn.close()
        return jsonify({'id': grade_id}), 201

@app.route('/api/grades/<int:grade_id>', methods=['DELETE'])
def grade_detail(grade_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM grades WHERE id = ?', (grade_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/flashcards', methods=['GET', 'POST'])
def flashcards():
    conn = get_db_connection()
    
    if request.method == 'GET':
        flashcards = conn.execute('SELECT * FROM flashcards ORDER BY created_at DESC').fetchall()
        conn.close()
        return jsonify([dict(row) for row in flashcards])
    
    elif request.method == 'POST':
        data = request.json
        conn.execute('''
            INSERT INTO flashcards (question, answer)
            VALUES (?, ?)
        ''', (data['question'], data['answer']))
        conn.commit()
        card_id = conn.lastrowid
        conn.close()
        return jsonify({'id': card_id}), 201

@app.route('/api/flashcards/<int:card_id>', methods=['DELETE'])
def flashcard_detail(card_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM flashcards WHERE id = ?', (card_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/stress-logs', methods=['GET', 'POST'])
def stress_logs():
    conn = get_db_connection()
    
    if request.method == 'GET':
        logs = conn.execute('SELECT * FROM stress_logs ORDER BY date DESC').fetchall()
        conn.close()
        return jsonify([dict(row) for row in logs])
    
    elif request.method == 'POST':
        data = request.json
        conn.execute('''
            INSERT OR REPLACE INTO stress_logs (date, stress_level, mood, notes, study_hours, sleep_hours)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['date'], data['stress_level'], data.get('mood'), 
              data.get('notes'), data.get('study_hours'), data.get('sleep_hours')))
        conn.commit()
        log_id = conn.lastrowid
        conn.close()
        return jsonify({'id': log_id}), 201

@app.route('/api/stress-logs/<int:log_id>', methods=['DELETE'])
def stress_log_detail(log_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM stress_logs WHERE id = ?', (log_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    conn = get_db_connection()
    
    if request.method == 'GET':
        settings = conn.execute('SELECT * FROM settings').fetchall()
        conn.close()
        return jsonify({row['key']: row['value'] for row in settings})
    
    elif request.method == 'POST':
        data = request.json
        for key, value in data.items():
            conn.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, str(value)))
        conn.commit()
        conn.close()
        return jsonify({'success': True})

@app.route('/api/initialize', methods=['POST'])
def initialize_data():
    """Initialize database with default requirements"""
    conn = get_db_connection()
    
    # Check if requirements already exist
    existing = conn.execute('SELECT COUNT(*) as count FROM requirements').fetchone()
    
    if existing['count'] == 0:
        # Add default requirements
        default_requirements = [
            ('ERV Letter (Year 1)', '2025-08-01', 'pending', 12),
            ('ERV Letter (Year 2)', '2026-08-01', 'pending', 12),
            ('Health Assessment Record', '2025-08-01', 'pending', 12),
            ('CPR-BLS', '2025-08-01', 'pending', 12),
            ('Standard First Aid', '2025-08-01', 'pending', 36),
            ('Mask Fit', '2025-08-01', 'pending', 24),
            ('Police Vulnerable Sector Check', '2025-08-01', 'pending', 12)
        ]
        
        for req in default_requirements:
            conn.execute('''
                INSERT INTO requirements (name, deadline, status, renewal_months)
                VALUES (?, ?, ?, ?)
            ''', req)
        
        # Set default current semester
        conn.execute('''
            INSERT OR REPLACE INTO settings (key, value)
            VALUES ('currentSemester', '1')
        ''')
        
        conn.commit()
    
    conn.close()
    return jsonify({'success': True})

@app.route('/')
def index():
    """Serve the main application HTML file"""
    with open('database_enabled_frontend.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/favicon_io/<path:filename>')
def favicon_files(filename):
    """Serve favicon files"""
    from flask import send_from_directory
    return send_from_directory('favicon_io', filename)

@app.route('/favicon.ico')
def favicon():
    """Serve favicon.ico from root"""
    from flask import send_from_directory
    return send_from_directory('favicon_io', 'favicon.ico')

@app.route('/api/backup', methods=['GET'])
def backup_data():
    """Export all data as JSON for backup"""
    conn = get_db_connection()
    
    backup = {
        'assignments': [dict(row) for row in conn.execute('SELECT * FROM assignments').fetchall()],
        'clinical_shifts': [dict(row) for row in conn.execute('SELECT * FROM clinical_shifts').fetchall()],
        'requirements': [dict(row) for row in conn.execute('SELECT * FROM requirements').fetchall()],
        'goals': [dict(row) for row in conn.execute('SELECT * FROM goals').fetchall()],
        'grades': [dict(row) for row in conn.execute('SELECT * FROM grades').fetchall()],
        'flashcards': [dict(row) for row in conn.execute('SELECT * FROM flashcards').fetchall()],
        'settings': {row['key']: row['value'] for row in conn.execute('SELECT * FROM settings').fetchall()},
        'backup_date': datetime.now().isoformat()
    }
    
    conn.close()
    return jsonify(backup)

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)