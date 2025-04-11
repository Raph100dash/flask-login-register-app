        pwd = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT Password, User, is_admin FROM login WHERE User = %s", (username,))
        user = cur.fetchone()
        cur.close()
        
        if user and pwd == user[0]:
            session['username'] = user[1]
            
            # Check if the user is the first user (admin)
            cur = mysql.connection.cursor()
            cur.execute("SELECT COUNT(*) FROM login")
            user_count = cur.fetchone()[0]
            cur.close()
            
            if user_count == 1:  # This is the first user in the database
                session['is_admin'] = True
                return redirect(url_for('admin'))  # Redirect to admin dashboard
            else:
                return redirect(url_for('home'))  # Redirect to the home page for regular users
            
        else:
            return render_template('login.html', error='Invalid user or password')
    
    return render_template('login.html')