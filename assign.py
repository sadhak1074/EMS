from flask import Flask, request, render_template
from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'managementapp'

mysql = MySQL(app)

# Create employee_project_assignment table
def create_employee_project_assignment_table():
    try:
        with app.app_context():
            cursor = mysql.connection.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS employee_project_assignment (
                              id INT AUTO_INCREMENT PRIMARY KEY,
                              employee_id INT,
                              project_id INT,
                              FOREIGN KEY (employee_id) REFERENCES usersdata(id),
                              FOREIGN KEY (project_id) REFERENCES projects(id)
                              )''')
            mysql.connection.commit()
            cursor.close()
    except Exception as e:
        print("Error:", e)

create_employee_project_assignment_table()

# Function to hash password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Function to verify password
def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Route to render the assignment form
@app.route('/assign', methods=['GET'])
def assign():
    with app.app_context():
        cursor = mysql.connection.cursor()
        # Fetch employee IDs and names from usersdata table
        cursor.execute("SELECT id, fullname FROM usersdata")
        employees = cursor.fetchall()
        # Fetch project IDs and names from projects table
        cursor.execute("SELECT id, project_name FROM projects")
        projects = cursor.fetchall()
        cursor.close()
    return render_template('assign_project.html', employees=employees, projects=projects)


# Route to handle project assignment
@app.route('/assign_project', methods=['POST'])
def assign_project():
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        project_id = request.form['project_id']

        # Insert assignment into employee_project_assignment table
        with app.app_context():
            cursor = mysql.connection.cursor()
            cursor.execute("""INSERT INTO employee_project_assignment (employee_id, project_id) 
                              VALUES (%s, %s)""", (employee_id, project_id))
            mysql.connection.commit()
            cursor.close()
        return 'Project assigned successfully'

if __name__ == '__main__':
    app.run(debug=True)
