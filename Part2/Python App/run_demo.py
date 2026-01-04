"""
Run Application in Demo Mode
Starts the application with SQLite demo database (no PostgreSQL required).
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Setup demo database first
print("Setting up demo database...")
try:
    from setup_demo_database import create_demo_database
    create_demo_database()
except Exception as e:
    print(f"Note: {e}")

# Run app in demo mode
print("\nStarting application in DEMO mode...")
print("(Using SQLite - no PostgreSQL required)\n")

# Add demo flag to arguments
sys.argv.append('--demo')

# Import and run main app
from App import main
main()

