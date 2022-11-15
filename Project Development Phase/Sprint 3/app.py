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