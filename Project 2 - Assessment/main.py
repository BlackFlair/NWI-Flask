from flask import Flask, render_template, request, url_for, session, g, redirect
import sqlite3
import os

currentDirectory = os.path.dirname(os.path.abspath(__file__))

db = "\database.db"

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/', methods=['GET', 'POST'])
def index():
    session.pop('user', None)
    if request.method == 'POST':
        session.pop('user', None)

        connection = sqlite3.connect(currentDirectory + db)
        cursor = connection.cursor()

        query = '''SELECT Password FROM Login WHERE Name = "{n}"'''.format(n=request.form['userName'])
        try:
            pwd = cursor.execute(query)
            pwd = pwd.fetchone()[0]
        except sqlite3.Error as e:
            print(e)

        if request.form['password'] == pwd:
            session['user'] = request.form['userName']  # userName : name given in html component for user name field
            return redirect(url_for('home'))
        else:
            print("Invalid Password.")

    return render_template('index.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    print(g.user)
    return render_template('home.html')


@app.before_request
def beforeRequest():
    g.user = None

    if 'user' in session:
        g.user = session['user']


@app.route('/dropSession')
def dropSession():
    session.pop('user', None)

    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)