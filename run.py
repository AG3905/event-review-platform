#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env for local development
load_dotenv()

# Ensure the project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Run the application (development)
    app.run(debug=os.environ.get('FLASK_DEBUG', 'True') == 'True', host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
