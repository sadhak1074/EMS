from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'managementapp'

mysql = MySQL(app)

# Create or update the table to include the 'status' column with a default value of 1
def create_or_update_table():
    try:
        with app.app_context():
            cursor = mysql.connection.cursor()
            # Create the table if it doesn't exist
            cursor.execute('''CREATE TABLE IF NOT EXISTS usersdata (
                              id INT AUTO_INCREMENT PRIMARY KEY,
                              fullname VARCHAR(255),
                              dob DATE,
                              qualification VARCHAR(255),
                              current_address VARCHAR(255),
                              department VARCHAR(255),
                              position VARCHAR(255),
                              joining_date DATE,
                              profile_picture VARCHAR(255),
                              email VARCHAR(255) UNIQUE,
                              password VARCHAR(255),
                              total_experience INT,
                              last_company_name VARCHAR(255),
                              last_salary FLOAT,
                              total_projects INT,
                              projects_complete INT,
                              projects_pending INT,
                              total_leaves INT,
                              status VARCHAR(255) DEFAULT '1'
                              )''')
            # Check if the 'status' column exists, and add it with a default value if it doesn't
            cursor.execute("SHOW COLUMNS FROM usersdata LIKE 'status'")
            result = cursor.fetchone()
            if not result:
                cursor.execute("ALTER TABLE usersdata ADD COLUMN status VARCHAR(255) DEFAULT '1'")
            mysql.connection.commit()
            
            # Update existing records to set status to '1' where it is NULL
            cursor.execute("UPDATE usersdata SET status = '1' WHERE status IS NULL")
            mysql.connection.commit()
            
            cursor.close()
    except Exception as e:
        print("Error:", e)

create_or_update_table()

# Function to hash password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Function to verify password
def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    fullname = data['fullname']
    dob = data['dob']
    qualification = data['qualification']
    current_address = data['current_address']
    department = data['department']
    position = data['position']
    joining_date = data['joining_date']
    profile_picture = data['profile_picture']
    email = data['email']
    password = data['password']
    total_experience = data['total_experience']
    last_company_name = data['last_company_name']
    last_salary = data['last_salary']
    total_projects = data['total_projects']
    projects_complete = data['projects_complete']
    projects_pending = data['projects_pending']
    total_leaves = data['total_leaves']
    status = 1  # Default status for new user

    # Hash the password
    password = hash_password(password).decode('utf-8')

    try:
        with app.app_context():
            cursor = mysql.connection.cursor()
            cursor.execute("""INSERT INTO usersdata (fullname, dob, qualification, current_address, department, position, 
                                                    joining_date, profile_picture, email, password, total_experience, 
                                                    last_company_name, last_salary, total_projects, projects_complete, 
                                                    projects_pending, total_leaves, status) 
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
                           (fullname, dob, qualification, current_address, department, position, joining_date, 
                            profile_picture, email, password, total_experience, last_company_name, last_salary, 
                            total_projects, projects_complete, projects_pending, total_leaves, status))
            mysql.connection.commit()
            cursor.close()
        return jsonify({'success': True, 'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data['email']
    password = data['password']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, password FROM usersdata WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    if user and verify_password(password, user[1]):
        session['logged_in'] = True
        session['user_id'] = user[0]
        return jsonify({'success': True, 'message': 'Logged in successfully'}), 200
    else:
        return jsonify({'error': 'Unauthorized', 'message': 'Invalid email or password'}), 401

@app.route('/dashboard')
def dashboard():
    if 'logged_in' in session:
        return jsonify({'message': 'You are logged in!'})
    else:
        return jsonify({'error': 'Unauthorized', 'message': 'Please login to access this page'}), 401

@app.route('/profile')
def profile():
    if 'logged_in' in session:
        user_id = session['user_id']
        with app.app_context():
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM usersdata WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
        return jsonify(user)
    else:
        return jsonify({'error': 'Unauthorized', 'message': 'Please login to access this page'}), 401

if __name__ == '__main__':
    app.run(debug=True)
