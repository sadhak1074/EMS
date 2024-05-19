from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'managementapp'

mysql = MySQL(app)

@app.route('/api/update_status/<int:user_id>', methods=['PUT'])
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

if __name__ == '__main__':
    app.run(debug=True)
