from flask import Flask, jsonify, request, render_template
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'managementapp'

mysql = MySQL(app)

@app.route('/api/users/<int:user_id>', methods=['GET', 'POST'])
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

if __name__ == '__main__':
    app.run(debug=True)
