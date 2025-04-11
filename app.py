from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor  

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'flaskusers'

mysql = MySQL(app)

# Get user details 
def get_user_details_from_db(username):
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT User, email, phone_number FROM login WHERE User = %s", (username,))
    user = cur.fetchone()
    cur.close()
    return user

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    is_admin = session.get('is_admin')

    if is_admin == 1:
        # ADMIN: Show all users in the login table
        cur = mysql.connection.cursor(cursorclass=DictCursor)
        cur.execute("SELECT personID, firstname, lastname, phone_number, email, User, is_admin FROM login")
        users = cur.fetchall()
        cur.close()
        return render_template('admin.html', username=username, users=users)
    else:
        # REGULAR USER: Show just their own info
        user_details = get_user_details_from_db(username)
        return render_template('home.html', username=username, user=user_details)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        cur = mysql.connection.cursor(cursorclass=DictCursor)
        cur.execute("SELECT Password, User, is_admin FROM login WHERE User = %s", (username,))
        user = cur.fetchone()
        cur.close()
        if user and pwd == user['Password']:
            session['username'] = user['User']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid user or password')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form['Firstname']
        lastname = request.form['Lastname']
        phone = request.form['Phone number']
        email = request.form['Email']
        username = request.form['username']
        pwd = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO login (firstname, lastname, phone_number, email, User, Password, is_admin) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (firstname, lastname, phone, email, username, pwd, 0)  # is_admin = 0 by default
        )
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('is_admin', None)
    return redirect(url_for('login'))

from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('is_admin') != 1:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin-dashboard')
def admin_dashboard():
    if session.get('is_admin') != 1:
        return redirect(url_for('home'))

    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT personID, firstname, lastname, phone_number, email, User, is_admin FROM login")
    users = cur.fetchall()
    cur.close()

    return render_template('admin.html', users=users)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'username' not in session or session.get('is_admin') != 1:
        return redirect(url_for('login'))  # Ensure only admin can access this

    # Fetch the user details from the database
    cur = mysql.connection.cursor(cursorclass=DictCursor)
    cur.execute("SELECT * FROM login WHERE personID = %s", (user_id,))
    user = cur.fetchone()

    if request.method == 'POST':
        # Get form data
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        phone = request.form['phone']
        email = request.form['email']
        username = request.form['username']
        is_admin = 1 if request.form.get('is_admin') else 0  # Admin checkbox
        
        # Update the user data in the database
        cur.execute("""
            UPDATE login SET firstname = %s, lastname = %s, phone_number = %s, email = %s, User = %s, is_admin = %s
            WHERE personID = %s
        """, (firstname, lastname, phone, email, username, is_admin, user_id))
        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard after update

    return render_template('edit_user.html', user=user)  # Show edit form with current user data

@app.route('/delete_user/<int:user_id>', methods=['GET'])
def delete_user(user_id):
    if 'username' not in session or session.get('is_admin') != 1:
        return redirect(url_for('login'))  # Ensure only admin can access this

    # Delete the user from the database
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM login WHERE personID = %s", (user_id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard after deletion

@app.route('/add_user', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        phone = request.form['phone']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        is_admin = 1 if request.form.get('is_admin') else 0

        cur = mysql.connection.cursor(cursorclass=DictCursor)
        cur.execute("""
            INSERT INTO login (firstname, lastname, phone_number, email, User, Password, is_admin)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (firstname, lastname, phone, email, username, password, is_admin))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('admin_dashboard'))

    return render_template('register_user.html')


if __name__ == '__main__':
    app.run(debug=True)

