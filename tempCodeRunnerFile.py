from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# mysql configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'  # Consider stronger passwords and env variables
app.config['MYSQL_DB'] = 'flaskusers'

mysql = MySQL(app)

@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT Password, User FROM login WHERE User = %s", (username,))
        user = cur.fetchone()
        cur.close()
        if user and pwd == user[0]:
            session['username'] = user[1]
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid user or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST']) # Added methods = ['GET', 'POST']
def register():
    if request.method == 'POST': # Corrected if statement
        username = request.form['username']
        pwd = request.form['password'] # Added password field
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO login (User, Password) VALUES (%s, %s)", (username, pwd)) # Corrected SQL and parameterized
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')  # Corrected route
def logout():
    session.pop('username', None) # corrected pop, and added None as default.
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)