from flask import Flask, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'managementapp'

mysql = MySQL(app)

@app.route('/api/users', methods=['GET'])
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

if __name__ == '__main__':
    app.run(debug=True)
