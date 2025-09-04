#!/usr/bin/env python3
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        from app.models import db
        db.create_all()

    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
