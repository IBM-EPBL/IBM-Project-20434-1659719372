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



# ADMIN LOGIN

@app.route("/adminlogin", methods =['GET', 'POST'])
def adminlogin():
    username = "admin"
    password = "@12345"
    message = ""
    if request.method == "POST" and "admin-uname" in request.form and "admin-pwd" in request.form:
        admin_uname = request.form['admin-uname']
        admin_pwd = request.form['admin-pwd']
        if admin_uname == username and admin_pwd == password:
            session['admin'] = admin_uname
            
            conn = db2_connection()
        
            # total agents
            stmt1 = "SELECT COUNT(*) FROM agent;"
            temp1 = ibm_db.exec_immediate(conn, stmt1)
            agents = ibm_db.fetch_tuple(temp1)
            
            # total complants
            stmt2 = "SELECT COUNT(*) FROM complaint;"
            temp2 = ibm_db.exec_immediate(conn, stmt2)
            complaints = ibm_db.fetch_tuple(temp2)
            
            # total assigned
            stmt3 = "SELECT COUNT(*) FROM complaint WHERE assignment='assigned';"
            temp3 = ibm_db.exec_immediate(conn, stmt3)
            assigned = ibm_db.fetch_tuple(temp3)
            
            # total unassigned
            stmt4 = "SELECT COUNT(*) FROM complaint WHERE assignment='not assigned';"
            temp4 = ibm_db.exec_immediate(conn, stmt4)
            unassigned = ibm_db.fetch_tuple(temp4)
            

            return render_template("admin-dashboard.html" , agents = agents, complaints = complaints, assigned = assigned, unassigned = unassigned)
        else:
            message = "Wrong user name and password!"
            return render_template("admin-login.html", message = message)
    else:
        return render_template("admin-login.html")
    
    

# admin dashboard
@app.route('/admindashboard')
def admindashboard():
    if session.get("admin") != None:
                    
        conn = db2_connection()
    
        # total agents
        stmt1 = "SELECT COUNT(*) FROM agent;"
        temp1 = ibm_db.exec_immediate(conn, stmt1)
        agents = ibm_db.fetch_tuple(temp1)
        
        # total complants
        stmt2 = "SELECT COUNT(*) FROM complaint;"
        temp2 = ibm_db.exec_immediate(conn, stmt2)
        complaints = ibm_db.fetch_tuple(temp2)
        
        # total assigned
        stmt3 = "SELECT COUNT(*) FROM complaint WHERE assignment='assigned';"
        temp3 = ibm_db.exec_immediate(conn, stmt3)
        assigned = ibm_db.fetch_tuple(temp3)
        
        # total unassigned
        stmt4 = "SELECT COUNT(*) FROM complaint WHERE assignment='not assigned';"
        temp4 = ibm_db.exec_immediate(conn, stmt4)
        unassigned = ibm_db.fetch_tuple(temp4)

        
        return render_template('admin-dashboard.html', agents = agents, complaints = complaints, assigned = assigned, unassigned = unassigned)
    else:
        return render_template("admin-login.html", message = "Session time out:( Please login!")




# admin add agent 

@app.route("/addagent", methods =['GET', 'POST'] )
def addagent():
    message = ""
    if session.get("admin") != None:
        if request.method == "POST" and 'agentid' in request.form and 'adob' in request.form and 'afname' in request.form and 'aemail' in request.form and 'aphoneno' in request.form and 'aaddress' in request.form and 'apwd' in request.form and 'acpwd' in request.form:
            agentid = request.form['agentid']
            a_dob = request.form['adob']
            a_fullname = request.form['afname']
            a_email = request.form['aemail']
            a_phoneno = request.form['aphoneno']
            a_address = request.form['aaddress']
            a_password = request.form['apwd']
            a_cpassword = request.form['acpwd']
            
            # checks agent already exists
            conn = db2_connection()
            stmt1 = "SELECT * FROM agent WHERE agentid='{}'".format(agentid)
            temp = ibm_db.exec_immediate(conn, stmt1)
            fetched = ibm_db.fetch_tuple(temp)
            ibm_db.close(conn)
            
            if fetched:
                message = 'Account already exists !'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', a_email):
                message = 'Invalid email address!'
            elif(a_password != a_cpassword):
                message = "Password not matched!"
            elif not a_phoneno.isnumeric():
                message = "Enter phone no correctly!"
            else:
                conn = db2_connection()
                stmt2 = "INSERT INTO agent VALUES ('{0}',' {1}','{2}', '{3}', '{4}', '{5}', '{6}');".format(agentid, a_fullname, a_dob, a_email, a_phoneno, a_address, a_password)
                ibm_db.exec_immediate(conn, stmt2)
                message = "Agent created successfully!"
                ibm_db.close(conn)
                return render_template('admin-add-agent.html', message = message)
        return render_template("admin-add-agent.html", message = message)
    return render_template("admin-login.html", message = "Session time out:( Please login!")




# view agents

@app.route("/viewagent")
def viewagent():
    if session.get("admin") != None:
        conn = db2_connection()
        stmt = "SELECT * FROM agent;"
        query = ibm_db.exec_immediate(conn, stmt)
        data = []
        while True:
            temp = ibm_db.fetch_tuple(query)
            if temp != False:
                data.append(temp)
            else:
                break
        print(data)
        return render_template("admin-view-agents.html", data = data)
    
    else:
        return render_template("admin-login.html", message = "session timed out:( please login again!")
 
 
 # remove agents
 
@app.route("/viewagent/remove")
def remove():
    if session.get("admin") != None:
        uid = request.args.get("id")
        conn = db2_connection()
        
        # delete agent
        stmt = f"DELETE FROM agent where agentid='{uid}'"
        ibm_db.exec_immediate(conn, stmt)
        
        message = "Agent deleted successfully!"       
        
        stmt1 = "SELECT * FROM agent;"
        query = ibm_db.exec_immediate(conn, stmt1)
        data = []
        while True:
            temp = ibm_db.fetch_tuple(query)
            if temp != False:
                data.append(temp)
            else:
                break
        return render_template("admin-view-agents.html", data = data, message = message)
    return render_template("admin-login", message = "session timed out:( please login again!")
 
 
 
# assign tasks to agent

@app.route("/assigntasks")       
def assigntasks():
    if session.get("admin") != None:
        conn = db2_connection()
        stmt1 = "SELECT * FROM complaint where assignment='not assigned';"
        query1 = ibm_db.exec_immediate(conn, stmt1)
        complaint = []
        while True:
            temp1 = ibm_db.fetch_tuple(query1)
            if temp1 != False:
                complaint.append(temp1)
            else:
                break
        stmt2 = "SELECT * FROM agent;"
        query2 = ibm_db.exec_immediate(conn, stmt2)
        agents = []
        while True:
            temp2 = ibm_db.fetch_tuple(query2)
            if temp2 != False:
                agents.append(temp2)
            else:
                break
        return render_template("admin-assign-tasks.html", complaint = complaint, agents = agents)
    else:
        return render_template("admin-login.html", message = "session timed out:( please login again!")
    



# tasks assignment

@app.route("/assigntasks/assign")
def assign():
    if session.get("admin") != None:
        
        aid = request.args.get('aid')
        cno = request.args.get('cno')
        
        if ( aid == 'Choose Agent'):
            conn = db2_connection()
            stmt1 = "SELECT * FROM complaint where assignment='not assigned';"
            query1 = ibm_db.exec_immediate(conn, stmt1)
            complaint = []
            while True:
                temp1 = ibm_db.fetch_tuple(query1)
                if temp1 != False:
                    complaint.append(temp1)
                else:
                    break
            stmt2 = "SELECT * FROM agent;"
            query2 = ibm_db.exec_immediate(conn, stmt2)
            agents = []
            while True:
                temp2 = ibm_db.fetch_tuple(query2)
                if temp2 != False:
                    agents.append(temp2)
                else:
                    break
            message = "Choose agent properly!"
            
        else:
        # assign table
            conn = db2_connection()
            stmt1 = f"update complaint set assignment='assigned', agentid='{aid}' where cno='{cno}';"
            ibm_db.exec_immediate(conn, stmt1)
            
            stmt1 = "SELECT * FROM complaint where assignment='not assigned';"
            query1 = ibm_db.exec_immediate(conn, stmt1)
            complaint = []
            while True:
                temp1 = ibm_db.fetch_tuple(query1)
                if temp1 != False:
                    complaint.append(temp1)
                else:
                    break
            stmt2 = "SELECT * FROM agent;"
            query2 = ibm_db.exec_immediate(conn, stmt2)
            agents = []
            while True:
                temp2 = ibm_db.fetch_tuple(query2)
                if temp2 != False:
                    agents.append(temp2)
                else:
                    break
            message = "Task assigned successfully!"
        return render_template("admin-assign-tasks.html", complaint = complaint, agents = agents, message = message)
    else:
        return render_template("admin-login.html", message = "session timed out:( please login again!")



# View assigned tasks

# @app.route('/viewassigned')
# def viewassigned():
#     if session.get("admin") != None:
#         conn = db2_connection()
        
#         # fetching assigned complaints
#         stmt = "SELECT * FROM complaint where assignment='assigned';"
#         query = ibm_db.exec_immediate(conn, stmt)
#         complaint = []
#         while True:
#             temp = ibm_db.fetch_tuple(query)
#             if (temp != False):
#                 complaint.append(temp)
#             else:
#                 break
            
#         # finding agentid by complaint no
#         for i in complaint:
#             stmt1 = f"SELECT * FROM assign where cno='{i[1]}'"
#             query1 = ibm_db.exec_immediate(conn, stmt1)
#             assignment = []
#             while True:
#                 temp1 = ibm_db.fetch_tuple(query1)
#                 if (temp1 != False):
#                     assignment.append(temp1)
                    
#         # finding respective agents by agentid
#         for j in assignment:
#             stmt2 = f"SELECT * FROM agent where agentid='{j[0]}'"
#             query2 = ibm_db.exec_immediate(conn, stmt2)
#             agents = []
#             while True:
#                 temp2 = ibm_db.fetch_tuple(query2)
#                 if (temp2 != False):
#                     agents.append(temp2)
                    
#         print(complaint)
#         print(assignment)
#         print(agents)
#         return render_template('admin-view-assigned-tasks.html')
#     else:
#         return render_template("admin-login.html", message = "session timed out:( please login again!")



# ADMIN LOGOUT

@app.route('/adminlogout')
def adminlogout():
    session.pop('admin', None)
    return redirect(url_for('adminlogin'))



# agent login

@app.route("/agentlogin", methods = ['GET', 'POST'])
def agentlogin():
    message = ''
    if request.method == 'POST':
        agentid = request.form['agentid']
        a_password = request.form['apassword']
        conn = db2_connection()            
        stmt2 = f"SELECT * FROM agent WHERE agentid='{agentid}' and apassword='{a_password}'"
        temp = ibm_db.exec_immediate(conn, stmt2)
        user = ibm_db.fetch_tuple(temp) 
                    
        if user:
            session['agentid'] = agentid
            session['agentname'] = user[1]
            conn = db2_connection()
            stmt = f"SELECT * FROM complaint WHERE agentid='{agentid}' and status='pending';"
            query = ibm_db.exec_immediate(conn, stmt)
            complaints = []
            while True:
                temp = ibm_db.fetch_tuple(query)
                if (temp != False):
                    complaints.append(temp)
                else:
                    break
    
            return render_template('agent-dashboard.html', agentname = f"{user[1]}", complaints = complaints)
        else:
            message = "Wrong agentid and password!"
            return render_template('agent-login.html', message = message)
            
    return render_template('agent-login.html', message = message)




# agent dashboard

@app.route("/agentdashboard")
def agentdashboard():
    if session.get('agentid') != None:
        agentid = session.get('agentid')
        agentname = session.get('agentname')
        conn = db2_connection()
        stmt = f"SELECT * FROM complaint WHERE agentid='{agentid}' and status='pending';"
        query = ibm_db.exec_immediate(conn, stmt)
        complaints = []
        while True:
            temp = ibm_db.fetch_tuple(query)
            if (temp != False):
                complaints.append(temp)
            else:
                break
        print(complaints)
        
        return render_template("agent-dashboard.html" , agentname = agentname, complaints = complaints)
    else:
        return render_template("agent-login.html", message = "session timed out:( please login again!")

        
@app.route('/agentprocess')
def agentprocess():
    if session.get('agentid') != None:
        agentid = session.get('agentid')
        agentname = session.get('agentname')
        csid = request.args.get('csid')
        cfid = request.args.get('cfid')
        conn = db2_connection()
        
        # success    
        if csid:
            stmt =  f"UPDATE complaint SET status='success' where agentid='{agentid}'and cno='{csid}';"
            ibm_db.exec_immediate(conn, stmt)
        
        # failure
        elif cfid:
            stmt1 = f"UPDATE complaint SET status='failure' where agentid='{agentid}' and cno='{cfid}';"
            ibm_db.exec_immediate(conn, stmt1)
            
        message = "Work completed!"
            
        stmt = f"SELECT * FROM complaint WHERE agentid='{agentid}' and status='pending';"
        query = ibm_db.exec_immediate(conn, stmt)
        complaints = []
        while True:
            temp = ibm_db.fetch_tuple(query)
            if (temp != False):
                complaints.append(temp)
            else:
                break
            
        return render_template("agent-dashboard.html", agentname = agentname, complaints = complaints, message = message )
    else:
        return render_template("agent-login.html", message = "session timed out:( please login again!")
        


# agent history

@app.route("/agenthistory")
def agenthistory():
    if session.get('agentid') != None:
        conn = db2_connection()
        
        agentid = session.get('agentid')
        agentname = session.get('agentname')
        
        stmt = f"SELECT * FROM complaint WHERE agentid='{agentid}';"
        query = ibm_db.exec_immediate(conn, stmt)
        complaints = []
        while True:
            temp = ibm_db.fetch_tuple(query)
            if (temp != False):
                complaints.append(temp)
            else:
                break
        return render_template("agent-history.html", agentname = agentname, complaints = complaints)
    else:
        return render_template("agent-login.html", message = "session timed out:( please login again!")





@app.route("/agentprofile")
def agentprofile():
    if session.get('agentid') != None:
        aid = session.get('agentid')
        print(aid)
        conn = db2_connection()
        stmt = f"SELECT * FROM agent where agentid='{aid}';"
        query = ibm_db.exec_immediate(conn, stmt)
        agents = []
        while True:
            temp = ibm_db.fetch_tuple(query)
            if (temp != False):
                agents.append(temp)  
            else:
                break          
        print(agents)
        return render_template("agent-profile.html", agents = agents)
    return render_template("agent-login.html", message="session timed out:( please login again!") 




        
# agent logout

@app.route("/agentlogout")
def agentlogout():
    del session['agentid']
    return render_template("agent-login.html")




if __name__ == "__main__":
    app.run(debug=True)