from flask import Flask, render_template, request, session, redirect, url_for
from database import register_user, login_user
from database import get_db_connection


app = Flask(__name__)
app.secret_key = 'super_secret_key_change_me_later'  # For sessions - make this random/strong in real app

@app.route('/')
def home():
    return '<h1>Flask is alive! Go to /register</h1>'

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        try:
            register_user(username, email, password)
            return redirect(url_for('login'))
        except ValueError as e:
            error = str(e)  # "Email already in use..."
        except Exception as e:
            error = "An unexpected error occurred. Please try again."
    
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("→ /login route was called (method:", request.method, ")")  # <--- add this

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = login_user(email, password)
        if user:
            session['user_id'] = user['user_id']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials"

    try:
        return render_template('login.html')
    except Exception as e:
        print("Template error:", str(e))
        return "<h2 style='color:red'>Template 'login.html' failed to load</h2><p>Error: " + str(e) + "</p>"

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/add_game', methods=['GET', 'POST'])
def add_game():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        genre = request.form.get('genre')
        release_year = request.form.get('release_year')
        summary = request.form.get('summary')

        # Simple DB insert (you can improve with duplicate check later)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Games (title, genre, release_year, summary) VALUES (%s, %s, %s, %s)",
            (title, genre, release_year, summary)
        )
        game_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO User_Games (user_id, game_id) VALUES (%s, %s)",
            (session['user_id'], game_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for('dashboard'))  # or show success message

    return render_template('add_game.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)