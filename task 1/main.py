from flask import Flask, redirect, render_template,request,session,jsonify
import psycopg2
import bcrypt

app = Flask(__name__)
app.secret_key = 'your-secret-key'

db_host = 'localhost'
db_name = 'infotrix'
db_user = 'postgres'
db_password = 'root@123'

def create_connection():
    try:
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password
        )
        return connection
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

@app.route('/')
def hello():
    username = session.get('username')
    if username is None:
        print("hello")
        return render_template('welcome.html')
    else:
        return redirect('/dashboard')



@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    print("Username: "+username)
    connection = create_connection()
    if connection is None:
        return redirect('/')

    cursor = connection.cursor()
    
    # Query the database for the username and password
    query = "SELECT * FROM info WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()


    # Check if the username and password are valid
    #print(result)
    if result is not None:
        stored_hashed_password = result[3]
        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
            print(bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')))
            session['username'] = result[1]  # Store username in session
            session['firstname'] = result[0]  # Store firstname in session
            session['lastname'] = result[2]  # Store lastname in session

            return redirect('dashboard')
        else:
            #print("None founf")
            return render_template('welcome.html',error_message='Incorrect password')
    else:
        return render_template('welcome.html',error_message='Username not found')


@app.route('/signup',methods= ['POST'])
def signup():
   
    username = request.form['signusername']
    password = request.form['signpassword']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    confirm_password = request.form['confirm_password']

        # Handle successful form submission here
        # ...
    connection = create_connection()
    if connection is None:
        return redirect('/')

    cursor = connection.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # Insert new user into the database
    query = "INSERT INTO info (username, password, firstname, lastname) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (username, hashed_password.decode('utf-8'), firstname, lastname))
    connection.commit()
    session['username'] = username  # Store username in session
    session['firstname'] = firstname  # Store firstname in session
    session['lastname'] = lastname
    return redirect('/dashboard')
    
    
    
    
@app.route('/dashboard')
def dashboard():
    username = session['username']
    firstname = session['firstname']
    lastname = session['lastname']
    return render_template('dashboard.html', user_id=username, firstname=firstname, lastname=lastname)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' in session:
        username = session['username']
        connection = create_connection()
        if connection is None:
            return jsonify({'success': False})

        cursor = connection.cursor()

        # Retrieve the new profile information from the AJAX request
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        # Update the profile information in the database
        query = "UPDATE info SET firstname = %s, lastname = %s, password = %s WHERE username = %s"
        cursor.execute(query, (firstName, lastName, hashed_password.decode('utf-8'), username))
        connection.commit()

        # Update the session variables with the new profile information
        session['firstname'] = firstName
        session['lastname'] = lastName

        return jsonify({'success': True})
    else:
        return jsonify({'success': False})

@app.route('/logout')
def logout():
    # Clear the session variables
    session.clear()

    # Redirect the user to the login page or any desired page
    return redirect('/')

app.run(debug=True)
