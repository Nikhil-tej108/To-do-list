from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)  # Required for session management
db = SQLAlchemy(app)

def ensure_db_exists():
    db_path = 'todo.db'
    if not os.path.exists(db_path):
        logger.info("Database file not found. Creating new database...")
        with app.app_context():
            db.create_all()
            logger.info("New database created successfully")
    else:
        logger.info("Database file exists")

def init_db():
    try:
        ensure_db_exists()
        with app.app_context():
            # Only create tables if they don't exist
            db.create_all()
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    todos = db.relationship('Todo', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'completed': self.completed,
            'created_at': self.created_at.strftime('%Y-%m-%d %I:%M %p')  # Format: 2024-03-14 02:30 PM
        }

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.get_json()
            logger.debug(f"Login attempt with data: {data}")
            
            # Validate input data
            if not data:
                logger.error("No data received in login request")
                return jsonify({'success': False, 'message': 'No data received'}), 400
                
            if 'email' not in data or not data['email']:
                logger.error("Email missing in login request")
                return jsonify({'success': False, 'message': 'Email is required'}), 400
                
            if 'password' not in data or not data['password']:
                logger.error("Password missing in login request")
                return jsonify({'success': False, 'message': 'Password is required'}), 400
            
            # Validate email format
            if '@' not in data['email'] or '.' not in data['email']:
                logger.error(f"Invalid email format: {data['email']}")
                return jsonify({'success': False, 'message': 'Invalid email format'}), 400
            
            # Find user and verify password
            user = User.query.filter_by(email=data['email']).first()
            if user and user.check_password(data['password']):
                session['user_id'] = user.id
                logger.info(f"Successfully logged in user: {data['email']}")
                return jsonify({'success': True})
            
            logger.warning(f"Failed login attempt for email: {data['email']}")
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
            
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return jsonify({'success': False, 'message': 'An error occurred during login'}), 500
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            data = request.get_json()
            logger.debug(f"Signup attempt with data: {data}")
            
            # Validate input data
            if not data:
                logger.error("No data received in signup request")
                return jsonify({'success': False, 'message': 'No data received'}), 400
                
            if 'email' not in data or not data['email']:
                logger.error("Email missing in signup request")
                return jsonify({'success': False, 'message': 'Email is required'}), 400
                
            if 'password' not in data or not data['password']:
                logger.error("Password missing in signup request")
                return jsonify({'success': False, 'message': 'Password is required'}), 400
            
            # Validate email format
            if '@' not in data['email'] or '.' not in data['email']:
                logger.error(f"Invalid email format: {data['email']}")
                return jsonify({'success': False, 'message': 'Invalid email format'}), 400
            
            # Check if email already exists
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                logger.warning(f"Email already registered: {data['email']}")
                return jsonify({'success': False, 'message': 'Email already registered'}), 400
            
            # Create new user
            user = User(email=data['email'])
            user.set_password(data['password'])
            
            try:
                db.session.add(user)
                db.session.commit()
                session['user_id'] = user.id
                logger.info(f"Successfully created user with email: {data['email']}")
                return jsonify({'success': True})
            except Exception as db_error:
                db.session.rollback()
                logger.error(f"Database error during signup: {str(db_error)}")
                return jsonify({'success': False, 'message': 'Database error occurred'}), 500
                
        except Exception as e:
            logger.error(f"Error during signup: {str(e)}")
            return jsonify({'success': False, 'message': 'An error occurred during signup'}), 500
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/api/todos', methods=['GET'])
def get_todos():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    todos = Todo.query.filter_by(user_id=session['user_id']).order_by(Todo.created_at.desc()).all()
    return jsonify([todo.to_dict() for todo in todos])

@app.route('/api/todos', methods=['POST'])
def add_todo():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    data = request.get_json()
    new_todo = Todo(title=data['title'], user_id=session['user_id'])
    db.session.add(new_todo)
    db.session.commit()
    return jsonify(new_todo.to_dict())

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    todo = Todo.query.filter_by(id=todo_id, user_id=session['user_id']).first_or_404()
    db.session.delete(todo)
    db.session.commit()
    return '', 204

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def toggle_todo(todo_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    todo = Todo.query.filter_by(id=todo_id, user_id=session['user_id']).first_or_404()
    todo.completed = not todo.completed
    db.session.commit()
    return jsonify(todo.to_dict())

if __name__ == '__main__':
    try:
        init_db()
        app.run(debug=True)
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}") 