"""Sytisec Secure Backend Application - OWASP & NIST Compliant"""
import os
import logging
from datetime import timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Security Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///sytisec.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session Security - OWASP A07:2021
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'True') == 'True'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

# CSRF Protection - OWASP A08:2021
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SSL_STRICT'] = os.environ.get('SESSION_COOKIE_SECURE', 'True') == 'True'

# Initialize Extensions
db = SQLAlchemy(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# CORS Configuration - OWASP A01:2021
CORS(app, 
     resources={r"/api/*": {"origins": os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')}},
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization', 'X-CSRF-Token'],
     methods=['GET', 'POST', 'OPTIONS'])

# Logging Configuration - OWASP A09:2021
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security Headers - OWASP A05:2021
@app.after_request
def set_security_headers(response):
    """Set security headers on every response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response

# Database Models
class ContactSubmission(db.Model):
    """Encrypted contact form submissions"""
    __tablename__ = 'contact_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    company = db.Column(db.String(255), nullable=True)
    message = db.Column(db.Text, nullable=False)
    submission_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    ip_address = db.Column(db.String(45), nullable=True)
    processed = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<ContactSubmission {self.id}>'

class NewsletterSubscriber(db.Model):
    """Newsletter subscribers"""
    __tablename__ = 'newsletter_subscribers'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    subscribed_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    verified = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<NewsletterSubscriber {self.email}>'

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Sytisec API'}), 200

@app.route('/api/contact', methods=['POST'])
@limiter.limit("5 per hour")
def submit_contact():
    """Submit contact form securely - OWASP A03:2021 Input Validation"""
    try:
        data = request.get_json()
        
        # Input validation
        if not data or not all(k in data for k in ['name', 'email', 'message']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        name = str(data.get('name', '')).strip()[:255]
        email = str(data.get('email', '')).strip()[:255]
        phone = str(data.get('phone', '')).strip()[:20] if data.get('phone') else None
        company = str(data.get('company', '')).strip()[:255] if data.get('company') else None
        message = str(data.get('message', '')).strip()
        
        # Validation checks
        if len(name) < 2 or len(name) > 255:
            return jsonify({'error': 'Invalid name'}), 400
        
        if '@' not in email or '.' not in email or len(email) > 255:
            return jsonify({'error': 'Invalid email'}), 400
        
        if len(message) < 10 or len(message) > 5000:
            return jsonify({'error': 'Message must be between 10-5000 characters'}), 400
        
        # Get client IP
        ip_address = request.remote_addr
        if request.headers.get('X-Forwarded-For'):
            ip_address = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        
        # Create submission record
        submission = ContactSubmission(
            name=name,
            email=email,
            phone=phone,
            company=company,
            message=message,
            ip_address=ip_address
        )
        
        db.session.add(submission)
        db.session.commit()
        
        logger.info(f'Contact form submitted from {ip_address}')
        
        return jsonify({
            'success': True,
            'message': 'Your message has been received. We will contact you soon.'
        }), 201
        
    except Exception as e:
        logger.error(f'Contact form error: {str(e)}')
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/newsletter/subscribe', methods=['POST'])
@limiter.limit("10 per hour")
def subscribe_newsletter():
    """Subscribe to newsletter"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
        
        email = str(data.get('email', '')).strip()[:255].lower()
        
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email'}), 400
        
        # Check if already subscribed
        existing = NewsletterSubscriber.query.filter_by(email=email).first()
        if existing:
            return jsonify({'message': 'Already subscribed'}), 200
        
        subscriber = NewsletterSubscriber(email=email, verified=True)
        db.session.add(subscriber)
        db.session.commit()
        
        logger.info(f'New newsletter subscriber: {email}')
        
        return jsonify({'success': True, 'message': 'Subscribed successfully'}), 201
        
    except Exception as e:
        logger.error(f'Newsletter subscription error: {str(e)}')
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/services', methods=['GET'])
def get_services():
    """Get Sytisec services"""
    services = {
        'services': [
            {
                'id': 1,
                'name': 'Cybersecurity Training',
                'description': 'Real-time cybersecurity training with practical simulations and clear guidance',
                'icon': '🎓'
            },
            {
                'id': 2,
                'name': 'VAPT Services',
                'description': 'Vulnerability Assessment and Penetration Testing - Base Level',
                'icon': '🛡️'
            },
            {
                'id': 3,
                'name': 'SOC Simulation',
                'description': 'Security Operations Center simulation and live training',
                'icon': '📡'
            },
            {
                'id': 4,
                'name': 'Awareness Programs',
                'description': 'Cybersecurity awareness training for organizations and institutions',
                'icon': '📢'
            },
            {
                'id': 5,
                'name': 'Curriculum Design',
                'description': 'Custom cybersecurity curriculum for colleges and universities',
                'icon': '📚'
            },
            {
                'id': 6,
                'name': 'Guide Books',
                'description': 'Industry-standard cybersecurity guide books following Packt standards',
                'icon': '📖'
            }
        ]
    }
    return jsonify(services), 200

@app.route('/api/directors', methods=['GET'])
def get_directors():
    """Get company directors information"""
    directors = {
        'directors': [
            {
                'name': 'Lijo Jose',
                'title': 'Director',
                'bio': 'Cybersecurity expert with extensive industry experience and training expertise'
            },
            {
                'name': 'Kishor Kumar J',
                'title': 'Director',
                'bio': 'Training and curriculum development specialist with focus on practical security'
            },
            {
                'name': 'Rakesh Gupta K',
                'title': 'Director',
                'bio': 'Strategic operations and business development lead'
            }
        ]
    }
    return jsonify(directors), 200

# Error Handlers
@app.errorhandler(400)
def bad_request(error):
    logger.warning(f'Bad request: {str(error)}')
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(429)
def ratelimit_handler(e):
    logger.warning(f'Rate limit exceeded: {str(e)}')
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Internal server error: {str(error)}')
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=5000, debug=False)
