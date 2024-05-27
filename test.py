from flask import Flask, request, jsonify, g, Response, render_template
from flask_mysqldb import MySQL
import bcrypt
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'
jwt_secret = 'your_jwt_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'managementapp'

mysql = MySQL(app)

# Create or update the tables
def create_or_update_table():
    try:
        with app.app_context():
            cursor = mysql.connection.cursor()
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
            cursor.execute("SHOW COLUMNS FROM usersdata LIKE 'status'")
            result = cursor.fetchone()
            if not result:
                cursor.execute("ALTER TABLE usersdata ADD COLUMN status VARCHAR(255) DEFAULT '1'")
            mysql.connection.commit()

            cursor.execute("UPDATE usersdata SET status = '1' WHERE status IS NULL")
            mysql.connection.commit()
            
            cursor.close()
    except Exception as e:
        print("Error:", e)

def create_tokens_table():
    try:
        with app.app_context():
            cursor = mysql.connection.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS user_tokens (
                              id INT AUTO_INCREMENT PRIMARY KEY,
                              user_id INT,
                              token VARCHAR(512),
                              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                              FOREIGN KEY (user_id) REFERENCES usersdata(id) ON DELETE CASCADE
                              )''')
            mysql.connection.commit()
            cursor.close()
    except Exception as e:
        print("Error:", e)

create_or_update_table()
create_tokens_table()

# Function to hash password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Function to verify password
def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# JWT token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'error': 'Unauthorized', 'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            g.user_id = data['user_id']
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM user_tokens WHERE token = %s", (token,))
            result = cursor.fetchone()
            cursor.close()
            if not result:
                return jsonify({'error': 'Unauthorized', 'message': 'Token is invalid or expired'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Unauthorized', 'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Unauthorized', 'message': 'Token is invalid'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

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
        token = jwt.encode({'user_id': user[0], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, jwt_secret, algorithm="HS256")
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO user_tokens (user_id, token) VALUES (%s, %s)", (user[0], token))
            mysql.connection.commit()
            cursor.close()
        except Exception as e:
            return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500
        return jsonify({'success': True, 'token': token}), 200
    else:
        return jsonify({'error': 'Unauthorized', 'message': 'Invalid email or password'}), 401

@app.route('/logout', methods=['POST'])
@token_required
def logout():
    token = request.headers['Authorization'].split(" ")[1]
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM user_tokens WHERE token = %s", (token,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

@app.route('/dashboard')
@token_required
def dashboard():
    return jsonify({'message': 'You are logged in!', 'user_id': g.user_id})

@app.route('/profile')
@token_required
def profile():
    user_id = g.user_id
    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM usersdata WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
    return jsonify(user)

@app.route('/api/users/<int:user_id>', methods=['GET', 'POST'])
@token_required
def update_user_data(user_id):
    if request.method == 'GET':
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM usersdata WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            if user:
                return render_template('update_user.html', user=user)
            else:
                return jsonify({'error': 'User not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    elif request.method == 'POST':
        try:
            data = request.form
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE usersdata SET fullname = %s, dob = %s, qualification = %s, current_address = %s, department = %s, position = %s, joining_date = %s, profile_picture = %s, email = %s, total_experience = %s, last_company_name = %s, last_salary = %s, total_projects = %s, projects_complete = %s, projects_pending = %s, total_leaves = %s WHERE id = %s",
                           (data['fullname'], data['dob'], data['qualification'], data['current_address'], data['department'], data['position'], data['joining_date'], data['profile_picture'], data['email'], data['total_experience'], data['last_company_name'], data['last_salary'], data['total_projects'], data['projects_complete'], data['projects_pending'], data['total_leaves'], user_id))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'message': 'User data updated successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/update_status/<int:user_id>', methods=['PUT'])
@token_required
def api_update_status(user_id):
    if not request.json or 'status' not in request.json:
        return jsonify({'error': 'Bad Request', 'message': 'Status is required'}), 400

    status = request.json['status']
    
    if status not in ['0', '1']:
        return jsonify({'error': 'Bad Request', 'message': 'Status must be either "0" (inactive) or "1" (active)'}), 400

    try:
        with app.app_context():
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE usersdata SET status = %s WHERE id = %s", (status, user_id))
            mysql.connection.commit()
            cursor.close()
        return jsonify({'success': True, 'message': 'Status updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

@app.route('/api/users', methods=['GET'])
@token_required
def get_users():
    try:
        with app.app_context():
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT fullname, dob, qualification, department, position, profile_picture FROM usersdata")
            users = cursor.fetchall()
            cursor.close()

        user_list = []
        for user in users:
            user_dict = {
                'fullname': user[0],
                'dob': str(user[1]),
                'qualification': user[2],
                'department': user[3],
                'position': user[4],
                'profile_picture': user[5]
            }
            user_list.append(user_dict)
        
        return jsonify(user_list)

    except Exception as e:
        return jsonify({'error': str(e)})

def create_project_table():
    try:
        with app.app_context():
            cursor = mysql.connection.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS projects (
                              id INT AUTO_INCREMENT PRIMARY KEY,
                              project_name VARCHAR(255),
                              technology VARCHAR(255),
                              project_start_date DATE,
                              project_end_date DATE,
                              project_document VARCHAR(255),
                              other_document VARCHAR(255),
                              project_links VARCHAR(255)
                              )''')
            mysql.connection.commit()
            cursor.close()
    except Exception as e:
        print("Error:", e)

create_project_table()

@app.route('/add_project', methods=['POST'])
@token_required
def add_project():
    if request.method == 'POST':
        data = request.get_json()
        project_name = data.get('project_name')
        technology = data.get('technology')
        project_start_date = data.get('project_start_date')
        project_end_date = data.get('project_end_date')
        project_document = data.get('project_document')
        other_document = data.get('other_document')
        project_links = data.get('project_links')

        with app.app_context():
            cursor = mysql.connection.cursor()
            cursor.execute("""INSERT INTO projects (project_name, technology, project_start_date, project_end_date, 
                                                    project_document, other_document, project_links) 
                              VALUES (%s, %s, %s, %s, %s, %s, %s)""", 
                           (project_name, technology, project_start_date, project_end_date, 
                            project_document, other_document, project_links))
            mysql.connection.commit()
            cursor.close()
        return 'Project added successfully'

@app.route('/project/<int:project_id>', methods=['GET'])
@token_required
def get_project(project_id):
    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
        project = cursor.fetchone()
        cursor.close()
    if project:
        return jsonify({
            'id': project[0],
            'project_name': project[1],
            'technology': project[2],
            'project_start_date': str(project[3]),
            'project_end_date': str(project[4]),
            'project_document': project[5],
            'other_document': project[6],
            'project_links': project[7]
        })
    else:
        return 'Project not found'
    
@app.route('/update_project_details/<int:project_id>', methods=['PUT'])
@token_required
def update_project_details(project_id):
    data = request.get_json()
    project_name = data.get('project_name')
    technology = data.get('technology')
    project_start_date = data.get('project_start_date')
    project_end_date = data.get('project_end_date')
    project_document = data.get('project_document')
    other_document = data.get('other_document')
    project_links = data.get('project_links')

    # Update project details in the database
    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute("""UPDATE projects SET project_name = %s, technology = %s, 
                          project_start_date = %s, project_end_date = %s, 
                          project_document = %s, other_document = %s, project_links = %s 
                          WHERE id = %s""",
                       (project_name, technology, project_start_date, project_end_date, 
                        project_document, other_document, project_links, project_id))
        mysql.connection.commit()
        cursor.close()

    return 'Project details updated successfully'

@app.route('/projects', methods=['GET'])
@token_required
def get_projects():
    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM projects")
        projects = cursor.fetchall()
        cursor.close()
    project_list = []
    for project in projects:
        project_list.append({
            'id': project[0],
            'project_name': project[1],
            'technology': project[2],
            'project_start_date': str(project[3]),
            'project_end_date': str(project[4]),
            'project_document': project[5],
            'other_document': project[6],
            'project_links': project[7]
        })
    return jsonify(project_list)


if __name__ == '__main__':
    app.run(debug=True)
