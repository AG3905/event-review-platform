#!/usr/bin/env python3
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Run the application
    app.run(debug=os.environ.get('FLASK_DEBUG', 'True') == 'True', host='0.0.0.0', port=5000)
