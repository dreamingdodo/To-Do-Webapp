from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib
import os
import time
import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mysecretkey')

def create_tasks_table(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  description TEXT NOT NULL,
                  due_date DATE,
                  completed INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

@app.route('/test')
def test():
    conn = sqlite3.connect('Task_master.db')
    print('Connected to database')

    # Add a test user to the database
    username = 'test1'
    password = 'test'
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        print('Test user added to database')
    except Exception as e:
        print('Error adding test user:', e)
        conn.rollback()

    conn.close()
    return 'Test page'


#register the user by adding to users.db and make a new table in task_master.dbtodo
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Retrieve form values
        username = request.form["username"]
        password = request.form["password"]

        # Hash the password
        hashed_password = hashlib.sha256(password.encode("utf-8")).hexdigest()

        # Create a new row for the user in the users table
        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        try:
            # Insert the user into the database
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            print('User registered successfully')

            # Create a table for the user in the task_master database
            conn_task_master = sqlite3.connect('task_master.db')
            c_task_master = conn_task_master.cursor()
            c_task_master.execute(f"CREATE TABLE IF NOT EXISTS '{username}' (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT, completed INTEGER, due_date TEXT)")
            conn_task_master.commit()
            conn_task_master.close()
            print("Created users tasks table")

        except Exception as e:
            print('Error registering user:', e)
            conn.rollback()
            return redirect(url_for('login'))

        finally:
            conn.close()
            return redirect(url_for('login'))
        
    else:
        return render_template('register.html')



# Dictionary to keep track of login attempts and their timestamps
login_attempts = {}

# Log in a user
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if there have been multiple failed login attempts within a certain time window
        if username in login_attempts:
            last_attempt_time = login_attempts[username]
            cooldown_duration = 10  # Cool-down duration in seconds
            elapsed_time = time.time() - last_attempt_time

            if elapsed_time < cooldown_duration:
                cooldown_remaining = cooldown_duration - elapsed_time
                error_message = f"Too many login attempts. Please wait {cooldown_remaining:.0f} seconds."
                return render_template('login.html', error=error_message)

        # Hash the password to compare it with the stored hash
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        user = c.fetchone()
        conn.close()

        if user is not None:
            session['username'] = user[1]
            login_attempts.pop(username, None)  # Clear the login attempts for the user
            return redirect(url_for('index'))
        else:
            if username in login_attempts:
                login_attempts[username] = time.time()  # Update the timestamp for the failed attempt
            else:
                login_attempts[username] = time.time()  # Add a new entry for the failed attempt
            return render_template('login.html', error='Invalid username or password')

    else:
        return render_template('login.html')


# Log out the current user
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

#goto register page from login page
@app.route('/no_account', methods=['GET', 'POST'])
def no_account():
    return redirect(url_for('register'))

#goto login page from register page
@app.route('/much_account', methods=['GET', 'POST'])
def much_account():
    return redirect(url_for('login', _method='GET'))

# Index page, accessible only to logged-in users
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    # Fetch the user's dark mode preference
    conn_users = sqlite3.connect('users.db')
    c_users = conn_users.cursor()
    c_users.execute("SELECT dark_mode FROM users WHERE username = ?", (username,))
    user_row = c_users.fetchone()
    conn_users.close()

    # Determine the mode based on the dark mode preference
    dark_mode = bool(user_row[0]) if user_row else False

    sort_by = request.args.get('sort_by', 'due_date')
    # Get the tasks from task_master
    conn = sqlite3.connect('task_master.db')
    c = conn.cursor()
    c.execute("SELECT * FROM '{}' WHERE completed=0 ORDER BY {}".format(username, sort_by))
    incomplete_tasks = c.fetchall()
    c.execute("SELECT * FROM '{}' WHERE completed=1 ORDER BY {}".format(username, sort_by))
    completed_tasks = c.fetchall()
    conn.close()

    return render_template('index.html', incomplete_tasks=incomplete_tasks, completed_tasks=completed_tasks, dark_mode=dark_mode, display_date=display_date)

# Function to update the dark_mode preference for a user
def update_dark_mode_preference(username, dark_mode):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET dark_mode = ? WHERE username = ?", (dark_mode, username))
    conn.commit()
    conn.close()

# Function to retrieve the dark_mode preference for a user
def get_dark_mode_preference(username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT dark_mode FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

# Function to handle the dark mode preference route (GET and POST)
@app.route('/dark_mode', methods=['GET', 'POST'])
def dark_mode():
    if request.method == 'GET':
        username = session['username']
        dark_mode = get_dark_mode_preference(username)
        return {'dark_mode': dark_mode}

    if request.method == 'POST':
        username = session['username']
        data = request.get_json()
        dark_mode = data['dark_mode']
        update_dark_mode_preference(username, dark_mode)
        return {'success': True}
        
#add a task to incomplete
@app.route('/add', methods=['POST'])
def add():
    task = request.form['task']
    due_date = request.form['due_date']
    username = session['username']
    conn = sqlite3.connect('task_master.db')
    c = conn.cursor()
    c.execute(f"INSERT INTO '{username}' (task, completed, due_date) VALUES (?, ?, ?)", (task, False, due_date))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

#complete a task
@app.route('/complete/<id>', methods=['POST'])
def complete_task(id):
    username = session['username']
    conn = sqlite3.connect('task_master.db')
    c = conn.cursor()
    c.execute(f"UPDATE '{username}' SET completed = ? WHERE id = ?", (1, id))
    conn.commit()
    conn.close()
    return redirect('/')

#remove a task from complete tasks
@app.route('/remove/<id>', methods=['POST'])
def remove_task(id):
    username = session['username']
    conn = sqlite3.connect('task_master.db')
    c = conn.cursor()
    c.execute(f"DELETE FROM '{username}' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

#edit incomplete tasks
@app.route('/edit/<id>', methods=['POST'])
def edit_task(id):
    new_task = request.form['new_task']
    new_due_date = request.form['due_date']
    username = session['username']
    conn = sqlite3.connect('task_master.db')
    c = conn.cursor()
    c.execute(f"UPDATE '{username}' SET task = ?, due_date = ? WHERE id = ?", (new_task, new_due_date, id))
    conn.commit()
    conn.close()
    return redirect('/')

# function to display the date as tomorrow/today
def display_date(date_str):
    # convert the string to a datetime object
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    
    today = datetime.date.today()
    
    tomorrow = today + datetime.timedelta(days=1)
    
    # check if the date is tomorrow/Today
    if date == tomorrow:
        return 'Tomorrow'
    elif date == today:
        return 'Today'
    else:
        return date.strftime('%Y-%m-%d')

if __name__ == '__main__':
    app.run(debug=True)