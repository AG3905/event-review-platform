# Event Review Platform

## 1. Project Title and Aim

### Project Title
Event Review Platform

### Aim and Problem Solved
The Event Review Platform is a full-stack Flask web application designed for event organizers to collect, manage, and analyze audience feedback efficiently. Traditional feedback collection methods often suffer from low response rates, rigid survey forms, or complex attendee login requirements. This platform addresses those challenges by providing:
- Frictionless public review submissions where attendees scan a QR code or follow a unique link to rate events without needing to register or log in.
- Customizable, category-aware feedback forms allowing event organizers to configure up to 10 custom questions (rating, single-choice, multiple-choice, yes/no, or free text).
- Real-time moderation, live dashboard updates, demographic insights, and CSV exports to enable organizers to act on attendee feedback.
- Global administration and platform-wide monitoring capabilities for platform administrators.

### Target Audience and User Roles
- **Organizer**: Event host or manager who creates events, sets up question sets, generates shareable QR codes, views live analytics, moderates attendee reviews, and exports review data.
- **Platform Admin**: Superuser role with global platform visibility across all organizers, events, and reviews, accessible via administrative dashboards and analytics endpoints.
- **Public Reviewer (Attendee)**: Event attendee who accesses the event review page via a unique link or QR code, completes a multi-step review wizard (or single-page fallback), submits ratings and optional feedback, and browses approved public reviews.


## 2. Features

### For Event Organizers
- **User Authentication and Profile Management**: Registration, login with rate limiting, password changes, profile updates, and email-based password resets via signed tokens.
- **Event Management**: Create, edit, and delete events with attributes including title, category, description, venue, date, time, capacity, review status toggle, and custom category handling.
- **Custom Question Builder**: Add up to 10 active custom questions per event with support for rating scales (1-5), single-choice, multiple-choice, yes/no toggles, and text inputs.
- **Category-Aware Question Suggestions**: Automated question suggestions tailored to event types (Music, Comedy, Workshop, Conference, Sports, Wedding, Corporate, Other).
- **Reusable Question Templates**: Save customized question sets as reusable `SavedQuestionSet` templates across multiple events.
- **QR Code and Link Generation**: Dynamic PNG QR code generation (in-memory with optional disk storage) pointing to the unique review URL (`/review/<unique_code>`).
- **Review Moderation**: Approve, reject, feature, or delete reviews from the organizer dashboard or via dedicated REST API endpoints.
- **Live Background Updates**: Client-side background polling (15-second interval) to display real-time review submissions and count updates without reloading the page.
- **Organizer Analytics**: Per-event statistical summaries, star rating distributions, response rate calculations based on expected capacity, per-question response breakdowns, attendee town/state location counts, and top-word frequency analysis.
- **Data Export**: Export event review records, metadata, and dynamic question answers as CSV files.

### For Platform Admins
- **Global Console**: Administrative views listing all registered organizers, all created events, and all submitted reviews across the system.
- **Platform Analytics**: Aggregate metrics showing overall organizer count, event count, total review volume, and platform-average ratings.
- **Role Elevation**: Automatic promotion of an organizer account to Platform Admin role upon sign-in if the account email matches the configured `PLATFORM_ADMIN_EMAIL` environment variable.

### For Public Reviewers (Attendees)
- **No-Account Review Submission**: Access forms directly via short unique event codes without creating an account.
- **Multi-Step Review Wizard**: 4-stage step-by-step review interface (Rating -> Custom Questions -> About You -> Summary & Submit) with step navigation and progress bar.
- **Progressive Enhancement / No-JS Fallback**: Seamless single-page form rendering when JavaScript is disabled in the browser.
- **Private Location Feedback**: Optional town/city and state/province collection kept strictly private for organizer analytics and never displayed publicly.
- **Spam and Bot Mitigation**: Hidden honeypot field (`website`) to catch automated bots and IP-based rate limiting (10 reviews per hour).
- **Duplicate Submission Guard**: One-review-per-email constraint enforced at both model and database levels per event.
- **Public Review Browser**: Paginated public view (`/review/<unique_code>/browse`) showing approved reviews for the event.


## 3. Technology Stack

### Backend
- **Python**: 3.11 (specified in Dockerfile and render.yaml)
- **Framework**: Flask 2.3.3
- **WSGI Server**: Gunicorn 21.2.0
- **HTTP/Web Utility**: Werkzeug 2.3.7

### Database and ORM
- **ORM**: SQLAlchemy via Flask-SQLAlchemy 3.0.5
- **Migrations**: Flask-Migrate 4.0.5 (Alembic)
- **Database Engine (Production)**: PostgreSQL 15 via `psycopg2-binary` 2.9.9
- **Database Engine (Development)**: SQLite (`sqlite:///event_reviews.db`)

### Authentication and Security
- **Authentication**: Flask-Login 0.6.3
- **Form Handling & Validation**: Flask-WTF 1.1.1, WTForms 3.0.1, email_validator
- **Security Headers**: Flask-Talisman 1.1.0 (Content Security Policy)
- **Rate Limiting**: Flask-Limiter 3.5.0 (with optional Redis backend)
- **Bot Mitigation**: Cloudflare Turnstile integration support (`TURNSTILE_SITE_KEY`) and honeypot validation
- **Token Generation**: `itsdangerous` (URLSafeTimedSerializer for password resets)

### Supporting Libraries
- **QR Code Generation**: `qrcode` 7.4.2 and `Pillow` >=10.0.1
- **Email Delivery**: Flask-Mail 0.9.1
- **Environment Management**: `python-dotenv` 1.0.0
- **Date/Time Utilities**: `python-dateutil` 2.8.2 and standard `zoneinfo`
- **Error Tracking**: `sentry-sdk` 1.27.0 (with Flask integration)
- **Caching / Rate Limit Store**: Redis 7 via `redis` 4.6.0 python package

### Frontend
- **HTML/CSS**: HTML5 and Vanilla CSS3 (custom CSS variables, responsive flexbox/grid layout)
- **JavaScript**: Vanilla JavaScript (ES6+, Fetch API, multi-step wizard logic, live updates polling)

### Testing
- **Test Framework**: `pytest` 7.4.2
- **Flask Test Helpers**: `pytest-flask` 1.2.0
- **Code Coverage**: `pytest-cov` 4.1.0

### Deployment and Infrastructure
- **Containerization**: Docker (`FROM python:3.11-slim`), Docker Compose 3.8 (Web, PostgreSQL 15, Redis 7)
- **PaaS Deployment**: Render (`render.yaml`, `build.sh`, `Procfile`)


## 4. Database Schema

The database consists of 7 tables defined using SQLAlchemy ORM in `app/models.py` (`users`, `events`, `reviews`, `event_questions`, `review_answers`, `saved_question_sets`, and `alembic_version`).

![Database Schema Diagram](docs/screenshots/database_schema.png)


## 5. Architecture Diagram

![System Architecture Diagram](docs/screenshots/architecture_diagram.png)


## 6. Use Case Diagram

![Use Case Diagram](docs/screenshots/use_case_diagram.png)


## 7. Live Demo Link

- Live Demo: https://event-review-platform-ywq6.onrender.com/


## 8. Screenshots

Below are captured screenshots of the deployed Event Review Platform interface:

### Landing Page
![Landing Page](docs/screenshots/landing_page.png)

### Sign In Page
![Sign In Page](docs/screenshots/login_page.png)

### Registration Page
![Registration Page](docs/screenshots/register_page.png)

### Public Review Form Wizard
![Public Review Form](docs/screenshots/public_review_page.png)

### Review Submission Success
![Review Success Page](docs/screenshots/review_success_page.png)

### Organizer Event Dashboard & Analytics
![Organizer Event Dashboard](docs/screenshots/event_details_dashboard.png)

### Platform Admin Console
![Platform Admin Console](docs/screenshots/admin_console.png)


## 9. Project Structure

```
event_review_platform/
├── .agents/                 # Workspace-specific agent configurations
├── .env.example             # Template for environment variables
├── .env.template            # Short template for required environment keys
├── .gitignore               # Git file ignore rules
├── .pyre_configuration      # Pyre type checker configuration
├── DEPLOY.md                # Deployment guidelines and platform notes
├── Dockerfile               # Production container image definition (Python 3.11-slim)
├── Procfile                 # Process file for Heroku/Render Gunicorn startup
├── README.md                # Project documentation
├── build.sh                 # Build script for deployment (pip install + flask db upgrade)
├── docker-compose.yml       # Multi-container Compose config (Web, PostgreSQL 15, Redis 7)
├── docs/                    # Documentation assets
│   └── screenshots/         # Captured screenshots of the live deployed web app
├── pyrightconfig.json       # Pyright static analysis configuration
├── pytest.ini               # pytest runner settings
├── render.yaml              # Render blueprint deployment configuration
├── requirements.txt         # Python package dependency manifest
├── run.py                   # Local development server entrypoint
├── app/                     # Flask application package
│   ├── __init__.py          # App factory, extension setup, and blueprint registration
│   ├── decorators.py        # Authorization decorators (@admin_required, @organizer_required)
│   ├── forms.py             # WTForms forms for auth, event, review, and profile
│   ├── models.py            # SQLAlchemy database models (User, Event, Review, etc.)
│   ├── question_templates.py# Category question templates and helper functions
│   ├── utils.py             # Helpers for QR generation, CSV export, and text processing
│   ├── api/                 # API blueprint directory
│   │   ├── __init__.py      # API blueprint initialization
│   │   └── routes.py        # REST API routes (moderation, analytics, polling, saved sets)
│   ├── auth/                # Authentication blueprint directory
│   │   ├── __init__.py      # Auth blueprint initialization
│   │   └── routes.py        # Authentication routes (login, register, reset password)
│   ├── main/                # Main blueprint directory
│   │   ├── __init__.py      # Main blueprint initialization
│   │   └── routes.py        # Core application routes (dashboards, event CRUD, reviews)
│   ├── static/              # Static web assets
│   │   ├── css/             # Custom CSS stylesheets
│   │   └── js/              # Client-side JavaScript files
│   └── templates/           # Jinja2 HTML templates
│       ├── 404.html         # Custom 404 error page template
│       ├── 500.html         # Custom 500 error page template
│       ├── base.html        # Base layout template
│       ├── index.html       # Landing page template
│       ├── admin/           # Admin console templates
│       ├── auth/            # Authentication templates
│       ├── components/      # Shared template components
│       ├── dashboard/       # Organizer dashboard templates
│       └── review/          # Public review wizard and browse templates
├── migrations/              # Alembic database migration scripts
├── scripts/                 # Database seeding and utility scripts
│   └── seed_demo.py         # Seed script for generating demo data
└── tests/                   # Automated test suite
    ├── conftest.py          # Pytest fixtures and app setup
    ├── test_auth.py         # Tests for authentication routes
    ├── test_bot_mitigation.py # Tests for honeypot bot prevention
    ├── test_csv_export_dynamic.py # Tests for CSV export generation
    ├── test_custom_category.py # Tests for custom event categories
    ├── test_event_ownership.py # Tests for event authorization rules
    ├── test_event_questions.py # Tests for dynamic event question CRUD
    ├── test_file_generation.py # Tests for QR code and file utilities
    ├── test_live_update_endpoints.py # Tests for polling API endpoints
    ├── test_pagination.py  # Tests for query pagination
    ├── test_password_reset.py # Tests for password reset token flows
    ├── test_rate_limits.py  # Tests for endpoint rate limits
    ├── test_review_form_wizard_fallback.py # Tests for form wizard fallback
    ├── test_review_moderation_api.py # Tests for review moderation API
    ├── test_review_privacy.py # Tests for location privacy rules
    ├── test_review_submission.py # Tests for standard review submissions
    └── test_review_submission_dynamic.py # Tests for dynamic review answers
```


## 10. Installation Instructions

### Prerequisites
- Python 3.11 or higher
- Git
- Docker and Docker Compose (optional, for containerized local execution)

### Option 1: Standard Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd event_review_platform
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   - On Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```

4. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   Copy the example environment file to `.env`:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to configure desired variables:
   ```env
   FLASK_DEBUG=True
   PORT=5000
   SECRET_KEY=dev-secret-key-change-in-production
   PLATFORM_ADMIN_EMAIL=admin@example.com
   # DATABASE_URL=postgresql://user:password@localhost:5432/eventdb
   # RATELIMIT_STORAGE_URL=redis://localhost:6379/0
   ```

6. **Apply database migrations**
   ```bash
   flask db upgrade
   ```

7. **(Optional) Seed demo data**
   ```bash
   python scripts/seed_demo.py
   ```

8. **Run the application locally**
   ```bash
   python run.py
   ```
   Access the app at `http://localhost:5000`.

### Option 2: Docker Setup

Run the entire application stack (Web, PostgreSQL 15, Redis 7) using Docker Compose:

1. **Build and start services**
   ```bash
   docker-compose up --build
   ```

2. **Apply migrations inside the web container**
   ```bash
   docker-compose exec web flask db upgrade
   ```

3. **Access the application**
   Navigate to `http://localhost:8000`.

### Running Tests

Run the full automated test suite using `pytest`:

```bash
pytest
```

To run with coverage report:

```bash
pytest --cov=app
```


## 11. Deployment Instructions

This repository is configured for deployment on platforms such as **Render** (via `render.yaml`) or **Heroku** (via `Procfile`).

### Render Deployment (Automated via Blueprint)

1. Connect the repository to your Render account.
2. Render detects `render.yaml`, which configures:
   - **Runtime**: Python 3.11
   - **Build Command**: `bash build.sh` (installs dependencies and runs `flask db upgrade`)
   - **Start Command**: `gunicorn 'app:create_app()' -w 4 -b 0.0.0.0:$PORT --log-level info`
3. Configure the following environment variables in the Render Dashboard:
   - `DATABASE_URL`: Connection string for PostgreSQL (e.g. Supabase or Render PostgreSQL).
   - `SECRET_KEY`: Secure secret key generated for production session signing.
   - `PLATFORM_ADMIN_EMAIL`: Email of the organizer account to promote to Platform Admin on sign-in.
   - `FLASK_DEBUG`: Set to `False`.
   - `RATELIMIT_STORAGE_URL`: (Optional) Redis connection URL for distributed rate limiting.
   - `FILE_STORAGE_PATH`: (Optional) Path for persistent disk storage of QR codes and CSV exports.

### Manual / Generic Server Deployment

1. **Environment Setup**:
   Ensure Python 3.11 is installed on the host system.

2. **Build Step**:
   ```bash
   pip install -r requirements.txt
   export FLASK_APP=run.py
   flask db upgrade
   ```

3. **Production Startup (Gunicorn)**:
   ```bash
   gunicorn "app:create_app()" -w 4 -b 0.0.0.0:${PORT:-8000} --log-level info
   ```

4. **Health Check Endpoint**:
   Point your load balancer or host health monitor to `GET /health` (returns HTTP 200 `{"status": "ok"}`).


## 12. Security Features, Browser Support, Contributing, License, Support, Roadmap

### Security Features
- **CSRF Protection**: All forms utilize Flask-WTF CSRF token validation (`WTF_CSRF_ENABLED=True`).
- **Password Security**: Password hashing implemented via Werkzeug (`generate_password_hash` / `check_password_hash`).
- **HTTP Security Headers**: Content Security Policy (CSP) headers applied globally via Flask-Talisman.
- **Session and Cookie Security**: `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE='Lax'`, and secure cookie toggles in production.
- **Rate Limiting**: Configured via Flask-Limiter (`200 per day`, `50 per hour` default; strict `5 per minute; 20 per hour` on login; `10 per hour` on review submissions).
- **SQL Injection Prevention**: Data interactions managed securely via SQLAlchemy ORM parameterized queries.
- **Bot Mitigation**: Honeypot field validation (`website` input) on review forms.
- **Signed Tokens**: Time-limited signed tokens using `itsdangerous` URLSafeTimedSerializer for password reset workflows.
- **Location Data Privacy**: Reviewer town and state information is strictly isolated to organizer analytics and never rendered on public review pages.

### Browser Support
- Google Chrome (latest versions)
- Mozilla Firefox (latest versions)
- Apple Safari (latest versions)
- Microsoft Edge (latest versions)
- Mobile Browsers (iOS Safari, Android Chrome)

### Contributing
1. Fork the repository on GitHub.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request detailing your changes.

### License
This project is open-source software made available under the [MIT License](LICENSE).
*(Note: Standard boilerplate; an explicit LICENSE file may be added to the repository root as needed).*

### Support
For support, inquiries, or bug reports:
- Email: ganganiayush2@gmail.com
- Repository: Open an issue on the repository issue tracker.

### Roadmap
Future planned enhancements for the Event Review Platform:
- **Mobile Applications**: Native iOS and Android mobile apps for organizers and attendees.
- **Sentiment Analysis**: Machine learning integration for automated sentiment scoring on text reviews.
- **External API Integrations**: Connectors for popular event management platforms (Eventbrite, Meetup).
- **Multi-language Support**: Internationalization (i18n) for international events.
- **Advanced Content Moderation**: Automated AI-powered spam and toxic content detection.
- **White-label Solutions**: Customizable branding and domain aliasing for enterprise clients.
