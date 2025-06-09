import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('meals.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        meal_type = request.form['meal_type']
        description = request.form['description']
        conn = get_db_connection()
        conn.execute('INSERT INTO meals (date, time, meal_type, description) VALUES (?, ?, ?, ?)',
                     (date, time, meal_type, description))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn = get_db_connection()
    meals = conn.execute('SELECT * FROM meals ORDER BY date DESC, time DESC').fetchall()
    conn.close()
    return render_template('index.html', meals=meals)

if __name__ == '__main__':
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS meals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        time TEXT NOT NULL,
                        meal_type TEXT NOT NULL,
                        description TEXT NOT NULL
                    )''')
    conn.close()
    app.run(host='0.0.0.0', port=5000)
