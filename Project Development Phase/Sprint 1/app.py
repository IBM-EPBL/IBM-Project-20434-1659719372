from flask import Flask, render_template, request, redirect, url_for, session
from uuid import uuid4
from dotenv import load_dotenv
import ibm_db
import os
import re
import random

load_dotenv()


def db2_connection():
    host = os.environ["DBHOST"]
    uid = os.environ["DBUID"]
    pwd = os.environ["DBPWD"]
    ssl = os.environ["DBSSLCERT"]
    db = os.environ["DB"]
    port = os.environ["DBPORT"]
    conn = ibm_db.connect(f"DATABASE={db};HOSTNAME={host};PORT={port};SECURITY=SSL;SSLServerCertificate={ssl};UID={uid};PWD={pwd};", "", "" )
    return conn


app = Flask(__name__)

app.secret_key = "Secret Key@!"



# index page

@app.route("/")
def index():
    session.pop('admin', None)
    session.pop('uid', None)
    session.pop('agentid', None)
    return render_template("index.html")




# USER REGISTER

@app.route('/register', methods =['GET', 'POST'])
def register():
    message = ''
    username = ''
    if request.method == 'POST' and 'uname' in request.form and 'pwd' in request.form and 'email' in request.form and 'cpwd' in request.form and 'address' in request.form and 'phoneno' in request.form and 'dob' in request.form:
        uid = uuid4().hex
        username = request.form['uname']
        password = request.form['pwd']
        email = request.form['email']
        dob = request.form['dob']
        address = request.form['address']
        phoneno = request.form['phoneno']
        cpassword = request.form['cpwd']
        
        conn = db2_connection()
        stmt1 = "SELECT * FROM customer WHERE PHONENO='{}'".format(phoneno)
        temp = ibm_db.exec_immediate(conn, stmt1)
        fetched = ibm_db.fetch_tuple(temp)
        ibm_db.close(conn)
        
        
        if fetched:
            message = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address !'
        elif(password != cpassword):
            message = "Password not matched"
        elif not phoneno.isnumeric():
            message = "Enter phone no correctly!"
        else:
            conn = db2_connection()
            stmt2 = "INSERT INTO customer VALUES ('{0}',' {1}','{2}', '{3}', '{4}', '{5}', '{6}');".format(uid, username, email, dob, address, phoneno, password, )
            tup = ibm_db.exec_immediate(conn, stmt2)
            stmt3 = f"SELECT * FROM customer where phoneno='{phoneno}'"
            tup = ibm_db.exec_immediate(conn, stmt3)
            sess = ibm_db.fetch_tuple(tup)
            session['uid'] = sess[0]
            username = session['username'] = sess[1]
            ibm_db.close(conn)
            return render_template('user-send-complaint.html')
    return render_template('user-register.html', message = message, username = username)




# USER LOGIN 

@app.route('/login', methods =['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'phoneno' in request.form and 'password' in request.form:
        phoneno = request.form['phoneno']
        password = request.form['password']
        
        
        conn = db2_connection()            
        stmt2 = f"SELECT * FROM customer WHERE phoneno='{phoneno}' and password='{password}'"
        temp = ibm_db.exec_immediate(conn, stmt2)
        user = ibm_db.fetch_tuple(temp) 
        message = 'Not a user :( Register First!'
                    
        if user:
            session['uid'] = user[0]
            session['username'] = user[1]
            return render_template('user-send-complaint.html', username = user[1])
            
    return render_template('user-login.html', message = message)



# USER SEND COMPLAINT

@app.route("/complaint", methods =['GET', 'POST'])
def complaint():
    message = ''
    if session.get('uid') != None:
        username = session.get('username')
        if request.method == 'POST' and 'c-name' in request.form and 'c-phoneno' in request.form and 'c-sub' in request.form and 'c-body' in request.form :
            cname = request.form['c-name']
            cphoneno = request.form['c-phoneno']
            csub = request.form['c-sub']
            cbody = request.form['c-body']
            cno = random.randint(100, 100000)     
            if "'" in csub:
                message = 'Do not use apastraphie in subject and body area!'
            elif "'" in cbody:
                message = 'Do not use apastraphie in subject and body area!'
            elif not (cphoneno.isalnum()):
                message = "Enter phone number correctly!"
            else:
                conn = db2_connection()
                stmt1 = f"INSERT INTO complaint VALUES ('{session['uid']}','{cno}','{cname}','{cphoneno}', '{csub}', '{cbody}', 'pending', 'not assigned', NULL);"
                ibm_db.exec_immediate(conn, stmt1)
                message = "complaint sent successfully!"              
        return render_template("user-send-complaint.html", message = message, username = username)
    return render_template("user-login.html", message = "session timed out:( please login again!")



# USER VIEW STATUS

@app.route("/status", methods =['GET', 'POST'])
def status():
    username = session.get('username')
    if session.get('uid') != None:
        conn = db2_connection()
        stmt1 = f"SELECT * FROM complaint where uid='{session['uid']}'"
        query = ibm_db.exec_immediate(conn, stmt1)
        data = []
        while True:
            temp = ibm_db.fetch_tuple(query)
            if temp  != False:
                data.append(temp)
            else:
                break
        return render_template("user-view-status.html", data=data, username = username)
    
    return render_template("user-login.html", message="session timed out:( please login again!") 
     
        

@app.route("/userprofile")
def userprofile():
    if session.get('uid') != None:
        uid = session.get('uid')
        conn = db2_connection()
        stmt = f"SELECT * FROM customer where uid='{uid}';"
        query = ibm_db.exec_immediate(conn, stmt)
        customers = []
        while True:
            temp = ibm_db.fetch_tuple(query)
            if (temp != False):
                customers.append(temp)  
            else:
                break          
        
        return render_template("user-profile.html", customers = customers)
    return render_template("user-login.html", message="session timed out:( please login again!") 

        
        
        
        
        
        
# user logout     
        
@app.route('/logout')
def logout():
    del session['uid']
    del session['username']
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)