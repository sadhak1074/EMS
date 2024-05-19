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

@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        project_name = request.form['project_name']
        technology = request.form['technology']
        project_start_date = request.form['project_start_date']
        project_end_date = request.form['project_end_date']
        project_document = request.files['project_document']
        other_document = request.files['other_document']
        project_links = request.form['project_links']

        # Save file paths or perform other operations with files here

        with app.app_context():
            cursor = mysql.connection.cursor()
            cursor.execute("""INSERT INTO projects (project_name, technology, project_start_date, project_end_date, 
                                                    project_document, other_document, project_links) 
                              VALUES (%s, %s, %s, %s, %s, %s, %s)""", 
                           (project_name, technology, project_start_date, project_end_date, 
                            project_document.filename, other_document.filename, project_links))
            mysql.connection.commit()
            cursor.close()
        return 'Project added successfully'

    return render_template('add_project.html')

if __name__ == '__main__':
    app.run(debug=True)
