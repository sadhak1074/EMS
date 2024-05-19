from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import hashlib

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'managementapp'

mysql = MySQL(app)

# Create a table to store form data
def create_table():
    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS userdata (
                          id INT AUTO_INCREMENT PRIMARY KEY,
                          fullname VARCHAR(255),
                          dob DATE,
                          qualification VARCHAR(255),
                          current_address VARCHAR(255),
                          department VARCHAR(255),
                          position VARCHAR(255),
                          joining_date DATE,
                          profile_picture VARCHAR(255),
                          password VARCHAR(255),
                          total_experience INT,
                          last_company_name VARCHAR(255),
                          last_salary FLOAT,
                          total_projects INT,
                          projects_complete INT,
                          projects_pending INT,
                          total_leaves INT)''')
        mysql.connection.commit()
        cursor.close()

create_table()

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.get_json()
    fullname = data['fullname']
    dob = data['dob']
    qualification = data['qualification']
    current_address = data['current_address']
    department = data['department']
    position = data['position']
    joining_date = data['joining_date']
    profile_picture = data['profile_picture']
    password = data['password']
    total_experience = data['total_experience']
    last_company_name = data['last_company_name']
    last_salary = data['last_salary']
    total_projects = data['total_projects']
    projects_complete = data['projects_complete']
    projects_pending = data['projects_pending']
    total_leaves = data['total_leaves']
    
    # Hash the password
    password = hashlib.sha256(password.encode()).hexdigest()
    
    # Insert into database
    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO userdata (fullname, dob, qualification, current_address, department, position, joining_date, profile_picture, password, total_experience, last_company_name, last_salary, total_projects, projects_complete, projects_pending, total_leaves) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (fullname, dob, qualification, current_address, department, position, joining_date, profile_picture, password, total_experience, last_company_name, last_salary, total_projects, projects_complete, projects_pending, total_leaves))
        mysql.connection.commit()
        cursor.close()
    return jsonify({'message': 'User added successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)
