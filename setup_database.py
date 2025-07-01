"""
Database setup script for Render deployment.
This script will be executed during the build process.
"""
import os
import shutil
import sys
import sqlite3
from pathlib import Path

def setup_database():
    # Path to the database file that was committed
    source_db = Path('/opt/render/project/src/db.sqlite3.deploy')
    # Path where the database should be located
    target_db = Path('/opt/render/project/src/db.sqlite3')
    
    print(f"Current working directory: {os.getcwd()}")
    print(f"Source DB exists: {source_db.exists()}")
    print(f"Target DB exists: {target_db.exists()}")
    
    # Ensure the target directory exists
    target_db.parent.mkdir(parents=True, exist_ok=True)
    
    # If the deployment database exists, copy it
    if source_db.exists():
        print(f"Copying database from {source_db} to {target_db}")
        try:
            shutil.copy2(str(source_db), str(target_db))
            # Set proper permissions
            target_db.chmod(0o664)
            print("Database copy completed successfully!")
            
            # Verify the database
            try:
                conn = sqlite3.connect(str(target_db))
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"Found {len(tables)} tables in the database")
                conn.close()
                return True
            except sqlite3.Error as e:
                print(f"Error verifying database: {e}")
                return False
                
        except Exception as e:
            print(f"Error copying database: {e}")
            return False
    else:
        print("No source database found, a new one will be created.")
        # Create an empty database file if it doesn't exist
        if not target_db.exists():
            try:
                conn = sqlite3.connect(str(target_db))
                conn.close()
                target_db.chmod(0o664)
                print("Created a new empty database file.")
                return True
            except Exception as e:
                print(f"Error creating new database: {e}")
                return False
    return True

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
