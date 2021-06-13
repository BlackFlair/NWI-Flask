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
        finally:
            cursor.close()
            connection.close()

        if request.form['password'] == pwd:
            session['user'] = request.form['userName']  # userName : name given in html component for user name field
            return redirect(url_for('home'))
        else:
            print("Invalid Password.")

    return render_template('index.html')


@app.route('/home', methods=['GET', 'POST'])
def home():
    if g.user:

        connection = sqlite3.connect(currentDirectory + db)
        cursor = connection.cursor()

        ##########
        # To be executed once per Name in signup part
        a = []
        b = []
        q = '''UPDATE Todo SET List = "{a}", Due = "{b}" WHERE Name = "{n}"'''.format(a=a, b=b, n=g.user)

        cursor.execute(q)  # , (a, b, g.user))
        connection.commit()
        ##########

        query1 = '''SELECT List, Due FROM Todo WHERE Name = ?'''.format(n=g.user)

        query2 = '''UPDATE Todo SET List=?, Due=? WHERE Name = ?'''

        try:
            todoList = cursor.execute(query1)
            todoList = todoList.fetchall()
            # connection.commit()
            print('Todo List: ', todoList)
        except sqlite3.Error as e:
            print('sqlite3.Error:', e)

        if 'add' in request.form:
            # cursor = connection.cursor()
            x = [request.form['todo']]
            y = [request.form['due']]

            try:
                cursor.execute(query2, (todoList[0][0].append(x), todoList[0][1].append(y), g.user))
                # print('Todo list after add: ', todoList)
                connection.commit()
            except sqlite3.OperationalError as e:
                print(e)

        if 'complete' in request.form:
            complete = request.form['complete']
            del todoList[0][0][complete]
            del todoList[0][1][complete]

            try:
                cursor.execute(query2, (todoList[0][0], todoList[0][1], g.user))
                connection.commit()
            except sqlite3.OperationalError as e:
                print(e)

        return render_template('home.html', t=todoList[0])
    return render_template('index.html')


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
