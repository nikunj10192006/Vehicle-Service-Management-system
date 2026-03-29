from flask import Flask, render_template, request, redirect, session, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

# -------- MYSQL --------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Nikunj@#001",
    database="vehicle_db"
)

cursor = db.cursor(dictionary=True)

# -------- REGISTER --------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            return render_template('register.html', error="User exists")

        hashed = generate_password_hash(password)

        cursor.execute("INSERT INTO users (username,password) VALUES (%s,%s)", (username, hashed))
        db.commit()

        return redirect('/')

    return render_template('register.html')

# -------- LOGIN --------
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user'] = username
            return redirect('/dashboard')

        return render_template('login.html', error="Invalid login")

    return render_template('login.html')

# -------- DASHBOARD --------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template('index.html')

# -------- LOGOUT --------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# -------- API --------
@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    cursor.execute("SELECT * FROM vehicles")
    return jsonify(cursor.fetchall())


@app.route('/api/vehicles', methods=['POST'])
def add_vehicle():
    data = request.json

    sql = "INSERT INTO vehicles (make, model, year, vin, price, status) VALUES (%s,%s,%s,%s,%s,%s)"
    val = (data['make'], data['model'], data['year'], data['vin'], data['price'], data['status'])

    cursor.execute(sql, val)
    db.commit()

    return jsonify({'success': True})


@app.route('/api/vehicles/<int:id>', methods=['PUT'])
def update_vehicle(id):
    data = request.json

    sql = "UPDATE vehicles SET make=%s, model=%s, year=%s, vin=%s, price=%s, status=%s WHERE id=%s"
    val = (data['make'], data['model'], data['year'], data['vin'], data['price'], data['status'], id)

    cursor.execute(sql, val)
    db.commit()

    return jsonify({'success': True})


@app.route('/api/vehicles/<int:id>', methods=['DELETE'])
def delete_vehicle(id):
    cursor.execute("DELETE FROM vehicles WHERE id=%s", (id,))
    db.commit()

    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)