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
    
    
# ADMIN LOGOUT

@app.route('/adminlogout')
def adminlogout():
    session.pop('admin', None)
    return redirect(url_for('adminlogin'))

if __name__ == "__main__":
    app.run(debug=True)