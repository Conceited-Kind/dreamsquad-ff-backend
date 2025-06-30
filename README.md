# DreamSquad FF - Backend

This is the Flask-based REST API that powers the DreamSquad Fantasy Football web application. It handles user authentication, data synchronization with external APIs, and all core application logic.

## Features

-   **User Authentication:** Secure user registration and login using JWT (JSON Web Tokens).
-   **Player Management:** Syncs and manages a local database of football players from the API-Football service.
-   **Team Management:** Endpoints for drafting players, managing a team budget, and viewing a user's squad.
-   **League Management:** Logic for creating private leagues, joining with a code, leaving, deleting, and viewing league standings.
-   **Dashboard API:** A consolidated endpoint to provide all necessary data for the user's main dashboard.

## Tech Stack

-   **Framework:** Flask
-   **Database:** SQLAlchemy with Flask-Migrate (SQLite for local, PostgreSQL for production)
-   **Authentication:** Flask-JWT-Extended
-   **API Documentation:** Flasgger (Swagger UI)

## Local Setup and Installation

To run this project on your local machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone <your-backend-repo-url>
    cd dreamsquad-ff-backend
    ```

2.  **Set up a Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    -   Create a file named `.env` in the root of the project.
    -   Add the following lines, replacing the placeholders with your actual keys:
        ```
        SECRET_KEY='a_strong_random_secret_key'
        JWT_SECRET_KEY='another_strong_random_secret_key'
        SQLALCHEMY_DATABASE_URI='sqlite:///dreamsquad.db'
        API_FOOTBALL_KEY='your_api_football_key_here'
        ```

5.  **Create the Database:**
    -   Run the database creation script. This will create your `dreamsquad.db` file with all the necessary tables.
        ```bash
        python create_db.py
        ```

6.  **Run the development server:**
    ```bash
    python run.py
    ```
    -   The API will be available at `http://localhost:5000`.
    -   API documentation (Swagger UI) is available at `http://localhost:5000/apidocs/`.

