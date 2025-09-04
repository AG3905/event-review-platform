# Event Review Platform

A comprehensive web-based platform for event organizers to collect and manage audience feedback through streamlined review forms and QR codes.

## Features

### For Event Organizers
- **User Authentication**: Secure registration and login system
- **Event Management**: Create, edit, and manage events with detailed information
- **QR Code Generation**: Automatically generate QR codes for easy review access
- **Review Dashboard**: View and manage all reviews with filtering and sorting
- **Analytics**: Comprehensive analytics including rating distributions and trends
- **Data Export**: Export review data to CSV files
- **Review Moderation**: Approve, feature, and manage individual reviews

### For Attendees
- **Easy Access**: Scan QR codes or use direct links to access review forms
- **Multi-step Review Process**: Intuitive step-by-step review submission
- **Star Ratings**: Interactive 5-star rating system
- **Category Feedback**: Quick feedback on specific aspects (sound, venue, organization, etc.)
- **Written Reviews**: Optional detailed text feedback
- **Review Browsing**: View other attendees' reviews and ratings

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Authentication**: Flask-Login with secure password hashing
- **Forms**: Flask-WTF with CSRF protection
- **QR Codes**: Python qrcode library
- **Styling**: Custom CSS with responsive design

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd event_review_platform
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## Usage

### Getting Started

1. **Register an account** as an event organizer
2. **Create your first event** with all relevant details
3. **Generate and share** the QR code or review link with attendees
4. **Monitor reviews** through your dashboard
5. **Export data** for further analysis

### Creating Events

- Fill in event details including title, category, venue, and date
- Set expected capacity for response rate calculations
- Choose whether to allow reviews (can be toggled later)
- Get instant access to shareable QR codes and links

### Managing Reviews

- View all reviews in a centralized dashboard
- Filter reviews by rating, date, or approval status
- Feature important reviews for highlighting
- Respond to reviews (optional feature)
- Export review data as CSV files

### Review Process (Attendees)

1. **Access**: Scan QR code or click shared link
2. **Information**: Provide name, email, and attendee type
3. **Rating**: Select star rating with descriptive feedback
4. **Categories**: Choose applicable categories (Great Sound, Good Venue, etc.)
5. **Review**: Write optional detailed feedback
6. **Submit**: Confirm submission and view other reviews

## Project Structure

```
event_review_platform/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models
│   ├── forms.py                 # WTForms definitions
│   ├── utils.py                 # Utility functions
│   ├── auth/                    # Authentication blueprint
│   ├── main/                    # Main application routes
│   ├── api/                     # API endpoints
│   ├── static/                  # Static files (CSS, JS, images)
│   └── templates/               # Jinja2 templates
├── requirements.txt             # Python dependencies
├── run.py                      # Application entry point
└── README.md                   # This file
```

## Configuration

The application uses Flask's built-in configuration system. Key settings:

- **SECRET_KEY**: Used for session management and CSRF protection
- **SQLALCHEMY_DATABASE_URI**: Database connection string
- **WTF_CSRF_ENABLED**: CSRF protection toggle

For production deployment, ensure to:
- Change the SECRET_KEY to a secure random value
- Use a production database (PostgreSQL recommended)
- Enable HTTPS
- Set up proper logging

## Security Features

- **CSRF Protection**: All forms protected against CSRF attacks
- **Password Security**: Secure password hashing with Werkzeug
- **Input Validation**: Comprehensive server-side validation
- **Session Security**: Secure session management
- **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection
- **Rate Limiting**: Basic IP-based rate limiting for review submissions

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For support, please contact [your-email@example.com] or create an issue in the repository.

## Roadmap

### Future Enhancements
- **Mobile App**: Native iOS and Android applications
- **Advanced Analytics**: Machine learning-powered sentiment analysis
- **Integration APIs**: Connect with popular event management platforms
- **Multi-language Support**: Internationalization for global use
- **Advanced Moderation**: AI-powered spam and content filtering
- **White-label Solutions**: Custom branding for enterprise clients

---

Built with ❤️ using Flask and modern web technologies.
