from flask import Flask, jsonify, redirect, render_template, request, Response, url_for
from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
db = SQLAlchemy(app)

class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(18), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)

    def __init__(self, name, phone, gender):
        self.name = name
        self.phone = phone
        self.gender = gender

    def __repr__(self):
        return f"<Item {self.name}>"
    
def validate_data(data):
    name = data.get('name')
    phone = data.get('phone')
    gender = data.get('gender')
    
    if name is not None and (len(name) < 2 or len(name) > 16):
        return False
    if phone is not None and not isinstance(phone, int):
        return False
    if gender is not None and gender not in ('Male', 'Female'):
        return False
    return True

@app.route('/')
def indexPage():
    return render_template('index.html')

@app.get('/api/hello')
def helloController():
    return "Hello"

@app.get('/api/students')
def showAllStudents():
    # I will provide whole Student JSON
    students = Students.query.all()
    students_list = []
    for student in students:
        student_dict = {}
        student_dict['id'] = student.id
        student_dict['name'] = student.name
        student_dict['phone'] = student.phone
        student_dict['gender'] = student.gender
        students_list.append(student_dict)
    studentJSON = json.dumps(students_list)
    return Response(studentJSON, content_type='application/json', status=200)

@app.post('/api/students')
def newStudent():
    # Get JSON data from the request
    student_data = request.get_json()

    # Extract name, phone, and gender from the JSON data
    try:
        name = student_data['name']
        phone = student_data['phone']
        gender = student_data['gender']
    except KeyError as e:
        return Response(json.dumps({'error':'Please provide all the required properties!'}), content_type='application/json', status=400)

    if validate_data({'name':name, 'phone':phone, 'gender':gender}):
        # Create a new Student object and add it to the database
        new_student = Students(name=name, phone=phone, gender=gender)
        db.session.add(new_student)
        db.session.commit()

        # Return a success message
        return Response(json.dumps({'success':'Student has been added!'}), content_type='application/json', status=200)
    else:
        return Response(json.dumps({'error':'Unexpected data provided, please look at the schema!'}), content_type='application/json', status=400)

@app.get('/api/students/<int:studentID>')
def getStudent(studentID):
    student = Students.query.get(studentID)

    if student:
        # Convert the Student object to a dictionary
        student_dict = {
            'id': student.id,
            'name': student.name,
            'phone': student.phone,
            'gender': student.gender
        }
        return Response(json.dumps(student_dict), content_type='application/json')
    else:
        return Response(json.dumps({'error': 'Student not found'}), content_type='application/json', status=404)


@app.put('/api/students/<int:studentID>')
def updateStudent(studentID):
    # Get JSON data from the request
    student_data = request.get_json()

    # Check if the JSON data contains all the required fields
    if 'name' not in student_data or 'phone' not in student_data or 'gender' not in student_data:
        response_data = json.dumps({'error': 'Incomplete JSON data. Please provide name, phone, and gender.'})
        return Response(response_data, content_type='application/json', status=400)

    # Find the Student with the given ID
    student = Students.query.get(studentID)

    # If the Student is not found, return an error message
    if student is None:
        response_data = json.dumps({'error': 'Student not found.'})
        return Response(response_data, content_type='application/json', status=404)

    # Update the Student's data with the new JSON data
    student.name = student_data['name']
    student.phone = student_data['phone']
    student.gender = student_data['gender']
    
    if validate_data({'name':student_data['name'], 'phone':student_data['phone'], 'gender':student_data['gender']}):
        # Commit the changes to the database
        db.session.commit()

        # Return a success message
        response_data = json.dumps({'success': 'Student has been updated!'})
        return Response(response_data, content_type='application/json', status=200)
    else:
        return Response(json.dumps({'error':'Unexpected data provided, please look at the schema!'}), content_type='application/json', status=400)


@app.delete('/api/students/<int:studentID>')
def deleteStudent(studentID):
    # Find the Student with the given ID
    student = Students.query.get(studentID)

    # If the Student is not found, return an error message
    if student is None:
        response_data = json.dumps({'error': 'Student not found.'})
        return Response(response_data, content_type='application/json', status=404)

    # Delete the Student from the database
    db.session.delete(student)
    db.session.commit()

    # Return a success message
    response_data = json.dumps({'success': 'Student has been deleted!'})
    return Response(response_data, content_type='application/json', status=200)


@app.patch('/api/students/<int:studentID>')
def updateStudentPartially(studentID):
    # User will provide the part that he want's to update and I update that part of Student
    # ... using ID on URL
    student_data = request.get_json()
    student = Students.query.get(studentID)

    if student is None:
        return Response(json.dumps({'error':'Student not found!'}), status=404, content_type='application/json')
    if student_data is {}:
        return Response(json.dumps({'error':'The request is empty, please include data!'}), status=400, content_type='application/json')

    if validate_data(student_data):
        # Update the Student's data with the new JSON data
        if 'name' in student_data:
            student.name = student_data['name']
        if 'phone' in student_data:
            student.phone = student_data['phone']
        if 'gender' in student_data:
            student.gender = student_data['gender']

        # Commit the changes to the database
        db.session.commit()

        # Return a success message
        return Response(json.dumps({'success':'Student partially updated!'}), content_type='application/json', status=200)
    else:
        return Response(json.dumps({'error':'Unexpected data provided, please look at the schema!'}), content_type='application/json', status=400)

@app.get('/api/students/search')
def searchStudents():
    # Get JSON data from the request
    search_data = request.get_json()

    # Check if the JSON data contains at least one of the required fields (name or gender)
    if 'name' not in search_data and 'gender' not in search_data:
        response_data = json.dumps({'error': 'Please provide at least one search parameter: name or gender.'})
        return Response(response_data, content_type='application/json', status=400)

    # Prepare the query based on the provided search parameters
    query = Students.query

    if 'name' in search_data:
        query = query.filter(Students.name.contains(search_data['name']))
    
    if 'gender' in search_data:
        query = query.filter(Students.gender == search_data['gender'])

    # Execute the query and fetch the matching Students
    matching_students = query.all()

    # Prepare the response JSON
    students_list = []
    for student in matching_students:
        student_dict = {
            'id': student.id,
            'name': student.name,
            'phone': student.phone,
            'gender': student.gender
        }
        students_list.append(student_dict)

    response_data = {
        'count': len(students_list),
        'students': students_list
    }

    # Return the response JSON
    response_json = json.dumps(response_data)
    return Response(response_json, content_type='application/json', status=200)

# For WebView
@app.route('/view')
def webviewLand():
    students = Students.query.all()
    return render_template('webview.html', students=students)

@app.route('/students/addNew')
def studentAddNew():
    return render_template('addNewStudent.html')

@app.route('/students/<int:studentID>')
def viewStudent(studentID):
    student = Students.query.get(studentID)

    if student:
        # Convert the Student object to a dictionary
        student_dict = {
            'id': student.id,
            'name': student.name,
            'phone': student.phone,
            'gender': student.gender
        }
        return render_template('viewStudent.html', student=student)
    else:
        return Response(json.dumps({'error': 'Student not found'}), content_type='application/json', status=404)

@app.route('/students/edit/<int:studentID>')
def viewEditStudent(studentID):
    student = Students.query.get(studentID)

    if student:
        # Convert the Student object to a dictionary
        student_dict = {
            'id': student.id,
            'name': student.name,
            'phone': student.phone,
            'gender': student.gender
        }
        return render_template('editStudent.html', student=student)
    else:
        return Response(json.dumps({'error': 'Student not found'}), content_type='application/json', status=404)    

# Server error handling bellow
@app.errorhandler(400)
def bad_request_error(e):
    response_data = json.dumps({'error': 'Bad Request: The server could not understand the request due to invalid syntax.'})
    return Response(response_data, content_type='application/json', status=400)

@app.errorhandler(401)
def unauthorized_error(e):
    response_data = json.dumps({'error': 'Unauthorized: The request requires user authentication.'})
    return Response(response_data, content_type='application/json', status=401)

@app.errorhandler(403)
def forbidden_error(e):
    response_data = json.dumps({'error': 'Forbidden: The server understood the request, but it refuses to authorize it.'})
    return Response(response_data, content_type='application/json', status=403)

@app.errorhandler(404)
def not_found_error(e):
    response_data = json.dumps({'error': 'Not Found: The requested resource could not be found on the server.'})
    return Response(response_data, content_type='application/json', status=404)

@app.errorhandler(405)
def method_not_allowed_error(e):
    response_data = json.dumps({'error': 'Method Not Allowed: The request method is not allowed for the requested resource.'})
    return Response(response_data, content_type='application/json', status=405)

@app.errorhandler(500)
def internal_server_error(e):
    response_data = json.dumps({'error': 'Internal Server Error: The server encountered an unexpected condition that prevented it from fulfilling the request. Please try again later or contact the website administrator.'})
    return Response(response_data, content_type='application/json', status=500)

@app.errorhandler(OverflowError)
def handle_overflow_error(e):
    response = jsonify({'message': 'The value you entered is too large. Please try again with a smaller value.'})
    response.status_code = 400
    return response

@app.route('/api/docs')
def showDocs():
    return render_template('swaggerui.html')

if __name__ == '__main__':
    app.run()