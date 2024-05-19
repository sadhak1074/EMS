from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'managementapp'

mysql = MySQL(app)

# Create projects table
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

# Function to hash password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Function to verify password
def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

@app.route('/add_project', methods=['POST'])
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
