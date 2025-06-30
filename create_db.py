import os
from app import create_app, db

print("--- Database Creation Script ---")

# Define the path for the database file relative to the script
db_file = os.path.join(os.path.dirname(__file__), 'dreamsquad.db')

# Check if the database file already exists and delete it for a clean start
if os.path.exists(db_file):
    print(f"Deleting old database file: {db_file}")
    os.remove(db_file)
else:
    print("No old database file found. A new one will be created.")

# Create the Flask app instance to establish an application context
app = create_app()

# The 'with app.app_context()' block ensures that the application is
# properly configured before we interact with the database.
with app.app_context():
    print("Creating all database tables...")
    
    # This command uses your models.py to create all the tables
    db.create_all()
    
    print("Database tables created successfully.")
    print("You can now run the main application with 'python run.py'")

