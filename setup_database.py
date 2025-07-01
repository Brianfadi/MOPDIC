"""
Database setup script for Render deployment.
This script will be executed during the build process.
"""
import os
import shutil
from pathlib import Path

def setup_database():
    # Path to the database file that was committed
    source_db = Path(__file__).parent / 'db.sqlite3.deploy'
    # Path where the database should be located
    target_db = Path(__file__).parent / 'db.sqlite3'
    
    # If the deployment database exists and the target doesn't, copy it
    if source_db.exists() and not target_db.exists():
        print(f"Copying database from {source_db} to {target_db}")
        shutil.copy2(source_db, target_db)
        print("Database setup complete!")
    else:
        print("No database setup needed.")

if __name__ == "__main__":
    setup_database()
