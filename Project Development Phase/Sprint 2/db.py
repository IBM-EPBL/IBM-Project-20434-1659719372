from flask import Flask
from dotenv import load_dotenv
import ibm_db
import os

load_dotenv()

host = os.environ["DBHOST"]
uid = os.environ["DBUID"]
pwd = os.environ["DBPWD"]
ssl = os.environ["DBSSLCERT"]
db = os.environ["DB"]
port = os.environ["DBPORT"]



conn = ibm_db.connect(f"DATABASE={db};HOSTNAME={host};PORT={port};SECURITY=SSL;SSLServerCertificate={ssl};UID={uid};PWD={pwd};", "", "" )




statement = "CREATE TABLE customer(uid varchar(100) not null, username VARCHAR(100) NOT NULL, email VARCHAR(100) NOT NULL, dob VARCHAR(10) NOT NULL, address VARCHAR(200) NOT NULL, phoneno VARCHAR(100) NOT NULL, password VARCHAR(50) NOT NULL); "


statement1 = "CREATE TABLE complaint(uid VARCHAR(100) NOT NULL, cno VARCHAR(100) NOT NULL, cname VARCHAR(100) NOT NULL, cphoneno VARCHAR(20) NOT NULL, subject VARCHAR(2000) NOT NULL, body VARCHAR(5000) NOT NULL, status VARCHAR(500) not null, assignment VARCHAR(500) not null,  agentid VARCHAR(500) ); "

# statement = "CREATE TABLE agent(agentid VARCHAR(100) NOT NULL, afullname VARCHAR(100) NOT NULL, adob VARCHAR(20) NOT NULL, aemail VARCHAR(500) NOT NULL, aphoneno VARCHAR(500) NOT NULL, aaddress VARCHAR(500) NOT NULL, apassword VARCHAR(500) NOT NULL);"


# statement = "CREATE TABLE assign(agentid VARCHAR(100) NOT NULL, cno VARCHAR(100) NOT NULL); "



# ibm_db.exec_immediate(conn, statement)
ibm_db.exec_immediate(conn, statement1)

