# Flask Students API

This is a simple Flask app that provides an API to manage students. The app uses PostgreSQL as a database to store student information.

## Requirements

You'll need the following installed on your system to run this app:

- Python 3.7 or later
- PostgreSQL

## Python Dependencies

To install the required Python dependencies, run the following command:

```bash
pip install Flask Flask-SQLAlchemy psycopg2
```

## Database Setup

Create a PostgreSQL database and a table with the following SQL command:

```sql
CREATE TABLE students (  
  id SERIAL PRIMARY KEY,  
  name VARCHAR(18) NOT NULL,  
  phone INTEGER NOT NULL,  
  gender VARCHAR(10) NOT NULL,  
  created INTEGER NOT NULL,  
  modified INTEGER
);
```

Make sure to update the `app.config['SQLALCHEMY_DATABASE_URI']` in the start of Flask app code with the correct connection string for your PostgreSQL database.

## Running the App

To run the Flask app in your local system, execute the following command:

```bash
python app.py
```

The app will start running on [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## API Endpoints

The following API endpoints are available:

- `GET /api/hello`: A simple "Hello" endpoint for testing
- `GET /api/students`: Fetch all students
- `POST /api/students`: Create a new student
- `GET /api/students/<int:studentID>`: Fetch a specific student by ID
- `PUT /api/students/<int:studentID>`: Update a specific student by ID
- `DELETE /api/students/<int:studentID>`: Delete a specific student by ID
- `PATCH /api/students/<int:studentID>`: Update a specific student partially by ID
- `GET /api/students/search`: Search for students by name or gender

## Web Views

Additionally, the app provides web views for managing students:

- `/`: Home page
- `/view`: List all students
- `/students/addNew`: Add a new student
- `/students/<int:studentID>`: View a specific student by ID
- `/students/edit/<int:studentID>`: Edit a specific student by ID
- `/api/docs`: API documentation