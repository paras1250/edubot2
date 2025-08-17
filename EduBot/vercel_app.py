#!/usr/bin/env python3
"""
EduBot - Vercel WSGI Entry Point
Optimized for Vercel serverless deployment
"""

import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables
load_dotenv()

# Create Flask application
app = create_app()

# For Vercel serverless functions
if __name__ == '__main__':
    app.run()
