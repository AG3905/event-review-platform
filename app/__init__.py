from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()
talisman = Talisman()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

def create_app():
    app = Flask(__name__)

    # Configuration
    is_debug = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    app.debug = is_debug
    # Security-related cookie settings
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    app.config['SESSION_COOKIE_SECURE'] = not is_debug
    app.config['REMEMBER_COOKIE_SECURE'] = not is_debug
    
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key and not is_debug:
        raise RuntimeError("SECRET_KEY must be set in production environment!")
    app.config['SECRET_KEY'] = secret_key or 'default-dev-key-please-change'
    
    # Use the Render database URL if available, otherwise use SQLite
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///event_reviews.db')
    
    # Fix for Render's postgres:// URL (SQLAlchemy requires postgresql://)
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True

    # SQLAlchemy engine tuning for production (pool options only for non-SQLite)
    if not database_url.startswith('sqlite'):
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
            'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 20)),
            'pool_pre_ping': True,
        }
    else:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
        }

    # Rate limiter storage (use Redis in production)
    ratelimit_url = os.environ.get('RATELIMIT_STORAGE_URL')
    if ratelimit_url:
        app.config['RATELIMIT_STORAGE_URL'] = ratelimit_url

    # Logging setup
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/event_platform.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Event Review Platform startup')
        # Ensure logs also go to stdout for containerized platforms
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)

    # Sentry integration (optional)
    sentry_dsn = os.environ.get('SENTRY_DSN')
    if sentry_dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration

            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[FlaskIntegration()],
                traces_sample_rate=float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.0')),
                send_default_pii=False,
                environment=os.environ.get('FLASK_ENV', 'production' if not is_debug else 'development')
            )
            app.logger.info('Sentry initialized')
        except Exception:
            app.logger.exception('Failed to initialize Sentry')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure security headers
    csp = {
        'default-src': [
            '\'self\'',
            'https://cdn.jsdelivr.net',
            'https://cdnjs.cloudflare.com',
            'https://fonts.googleapis.com',
            'https://fonts.gstatic.com',
            'https://code.jquery.com'
        ]
    }
    talisman.init_app(app, content_security_policy=csp)
    limiter.init_app(app)

    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Import and register blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        from flask import render_template
        return render_template('500.html'), 500

    return app

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
