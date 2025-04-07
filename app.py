from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# mysql configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'  
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form['Firstname']  # Matching the HTML
        lastname = request.form['Lastname']   # Matching the HTML
        phone = request.form['Phone number']  # Matching the HTML
        email = request.form['Email']         # Matching the HTML
        username = request.form['username']
        pwd = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO login (firstname, lastname, phone_number, email, User, Password) VALUES (%s, %s, %s, %s, %s, %s)",
            (firstname, lastname, phone, email, username, pwd)
        )
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')  
def logout():
    session.pop('username', None) 
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)