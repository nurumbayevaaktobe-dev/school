from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import create_access_token, get_jwt_identity
import os
from datetime import datetime

# Import extensions
from extensions import db, socketio, cache, limiter, bcrypt, jwt, init_extensions
from config import config

# Import models
from models.user import User
from models.activity import Activity
from models.violation import Violation
from models.message import Message

# Import services
from services.ai_service import ai_service
from services.compression_service import compressor
from services.security_service import require_auth, rate_limit, ai_rate_limiter, screenshot_rate_limiter

def create_app(config_name='development'):
    """Create and configure Flask app"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Enable CORS
    CORS(app)

    # Initialize extensions
    init_extensions(app)

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

    # Authentication routes
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        """Register new user"""
        data = request.get_json()

        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400

        # Check if user exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400

        if User.query.filter_by(email=data.get('email', '')).first():
            return jsonify({'error': 'Email already exists'}), 400

        # Create user
        user = User(
            username=data['username'],
            email=data.get('email', ''),
            role=data.get('role', 'student')
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'User created successfully', 'user': user.to_dict()}), 201

    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """Login user"""
        data = request.get_json()

        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Missing credentials'}), 400

        user = User.query.filter_by(username=data['username']).first()

        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Create access token
        access_token = create_access_token(identity=user.id)

        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200

    # AI routes
    @app.route('/api/ai/classroom-insights', methods=['POST'])
    @require_auth(role='teacher')
    @rate_limit(ai_rate_limiter)
    def classroom_insights():
        """Get AI-powered classroom insights"""
        data = request.get_json()
        students_data = data.get('students', {})

        insights = ai_service.analyze_classroom(students_data)

        return jsonify(insights), 200

    @app.route('/api/ai/check-all-code', methods=['POST'])
    @require_auth(role='teacher')
    @rate_limit(ai_rate_limiter)
    def check_all_code():
        """Batch check code on all student screens"""
        data = request.get_json()
        students = data.get('students', [])
        language = data.get('language', 'python')

        results = ai_service.batch_check_code(students)

        return jsonify(results), 200

    @app.route('/api/ai/message-suggest', methods=['POST'])
    @require_auth(role='teacher')
    @rate_limit(ai_rate_limiter)
    def message_suggest():
        """Generate smart message suggestions"""
        data = request.get_json()

        suggestions = ai_service.generate_smart_message(data)

        return jsonify(suggestions), 200

    # SocketIO event handlers
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        print(f"Client connected: {request.sid}")
        emit('connected', {'session_id': request.sid})

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print(f"Client disconnected: {request.sid}")

        # Update user status
        user = User.query.filter_by(session_id=request.sid).first()
        if user:
            user.status = 'offline'
            user.last_seen = datetime.utcnow()
            db.session.commit()

    @socketio.on('register_student')
    def handle_register_student(data):
        """Register student agent"""
        print(f"Student registered: {data.get('name')}")

        # Find or create user
        user = User.query.filter_by(computer_id=data.get('computer_id')).first()

        if not user:
            # Create new student user
            user = User(
                username=data.get('name', f"student_{request.sid}"),
                email=f"{data.get('name', 'student')}@school.local",
                role='student',
                computer_id=data.get('computer_id')
            )
            user.set_password('default_password')  # Should be changed
            db.session.add(user)

        user.session_id = request.sid
        user.status = 'online'
        user.last_seen = datetime.utcnow()
        db.session.commit()

        # Join student room
        join_room('students')

        emit('registered', {'user_id': user.id, 'username': user.username})

        # Notify teachers
        emit('student_connected', {
            'user_id': user.id,
            'username': user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, room='teachers', broadcast=True)

    @socketio.on('register_teacher')
    def handle_register_teacher(data):
        """Register teacher client"""
        print(f"Teacher registered: {data.get('name')}")

        join_room('teachers')

        # Send current student list
        students = User.query.filter_by(role='student').all()
        emit('student_list', {
            'students': [s.to_dict() for s in students]
        })

    @socketio.on('screen_update')
    @rate_limit(screenshot_rate_limiter, key_func=lambda: request.sid)
    def handle_screen_update(data):
        """Handle screenshot update from student"""
        user = User.query.filter_by(session_id=request.sid).first()

        if not user:
            return

        # Compress image if needed
        screenshot = data.get('screenshot')
        if screenshot and not data.get('hash'):
            compressed, img_hash, size_kb = compressor.compress_base64(screenshot)
            data['screenshot'] = compressed
            data['hash'] = img_hash
            data['size_kb'] = size_kb

        # Save activity
        activity = Activity(
            user_id=user.id,
            screenshot_hash=data.get('hash'),
            active_window=data.get('active_window'),
            active_app=data.get('active_app')
        )
        db.session.add(activity)
        db.session.commit()

        # Broadcast to teachers
        emit('screen_data', {
            'user_id': user.id,
            'username': user.username,
            'image': data.get('screenshot'),
            'active_window': data.get('active_window'),
            'active_app': data.get('active_app'),
            'timestamp': datetime.utcnow().isoformat()
        }, room='teachers', broadcast=True)

    @socketio.on('process_update')
    def handle_process_update(data):
        """Handle process list update from student"""
        user = User.query.filter_by(session_id=request.sid).first()

        if not user:
            return

        # Check for violations
        processes = data.get('processes', [])
        urls = data.get('urls', [])

        # Simple violation detection
        violation_keywords = {
            'game': ['game', 'minecraft', 'fortnite', 'roblox'],
            'social_media': ['facebook', 'instagram', 'twitter', 'tiktok'],
            'video': ['youtube', 'netflix', 'twitch']
        }

        for v_type, keywords in violation_keywords.items():
            for process in processes:
                process_lower = process.lower()
                if any(keyword in process_lower for keyword in keywords):
                    violation = Violation(
                        user_id=user.id,
                        violation_type=v_type,
                        detail=f"Detected process: {process}"
                    )
                    db.session.add(violation)

            for url in urls:
                url_lower = url.lower()
                if any(keyword in url_lower for keyword in keywords):
                    violation = Violation(
                        user_id=user.id,
                        violation_type=v_type,
                        detail=f"Detected URL: {url}"
                    )
                    db.session.add(violation)

        db.session.commit()

    @socketio.on('send_message')
    def handle_send_message(data):
        """Send message to student(s)"""
        sender_user = User.query.filter_by(session_id=request.sid).first()

        if not sender_user or sender_user.role != 'teacher':
            return

        target = data.get('target', 'all')
        message_content = data.get('message', '')
        message_type = data.get('type', 'normal')

        if target == 'all':
            # Broadcast to all students
            emit('receive_message', {
                'message': message_content,
                'type': message_type,
                'from': sender_user.username,
                'timestamp': datetime.utcnow().isoformat()
            }, room='students', broadcast=True)
        else:
            # Send to specific student
            target_user = User.query.get(target)
            if target_user and target_user.session_id:
                emit('receive_message', {
                    'message': message_content,
                    'type': message_type,
                    'from': sender_user.username,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=target_user.session_id)

    @socketio.on('lock_screens')
    def handle_lock_screens(data):
        """Lock student screens"""
        sender_user = User.query.filter_by(session_id=request.sid).first()

        if not sender_user or sender_user.role != 'teacher':
            return

        students = data.get('students', 'all')
        duration = data.get('duration', 300)
        message = data.get('message', 'Screen locked by teacher')

        if students == 'all':
            emit('screen_lock', {
                'duration': duration,
                'message': message
            }, room='students', broadcast=True)
        else:
            for student_id in students:
                target_user = User.query.get(student_id)
                if target_user and target_user.session_id:
                    emit('screen_lock', {
                        'duration': duration,
                        'message': message
                    }, room=target_user.session_id)

    @socketio.on('unlock_screens')
    def handle_unlock_screens(data):
        """Unlock student screens"""
        sender_user = User.query.filter_by(session_id=request.sid).first()

        if not sender_user or sender_user.role != 'teacher':
            return

        students = data.get('students', 'all')

        if students == 'all':
            emit('screen_unlock', {}, room='students', broadcast=True)
        else:
            for student_id in students:
                target_user = User.query.get(student_id)
                if target_user and target_user.session_id:
                    emit('screen_unlock', {}, room=target_user.session_id)

    @socketio.on('create_poll')
    def handle_create_poll(data):
        """Create a poll for students"""
        sender_user = User.query.filter_by(session_id=request.sid).first()

        if not sender_user or sender_user.role != 'teacher':
            return

        question = data.get('question')
        options = data.get('options', [])

        poll_data = {
            'poll_id': f"poll_{datetime.utcnow().timestamp()}",
            'question': question,
            'options': options,
            'timestamp': datetime.utcnow().isoformat()
        }

        emit('show_poll', poll_data, room='students', broadcast=True)

    @socketio.on('poll_response')
    def handle_poll_response(data):
        """Handle poll response from student"""
        poll_id = data.get('poll_id')
        answer = data.get('answer')

        # Aggregate results and send to teacher
        emit('poll_results', {
            'poll_id': poll_id,
            'answer': answer,
            'timestamp': datetime.utcnow().isoformat()
        }, room='teachers', broadcast=True)

    return app

# Create app instance
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created")

    # Run app
    print("🚀 Starting AI ClassGuard Pro Server...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
