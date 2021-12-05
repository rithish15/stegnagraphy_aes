import pymysql
import requests
import json
import smtplib,ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import math
from flask import jsonify
import os


otp = "" 
mobile = ""
password = ""
username = ""

mydb = pymysql.connect(
  host="localhost",
  user="root",
  password="admin",
  database="connect"
)


def new_user(data): 
    global mydb
    mycursor = mydb.cursor()
    global otp,mobile,password,username
    mobile = data["mobile"]
    password = data["password"]
    username = data["name"]
    output = {"status": "success"}
    add_user_to_db()

    sql = "SELECT LAST_INSERT_ID()"
    mycursor.execute(sql)
    user_id = mycursor.fetchone()
    print(user_id)
    directory = str(user_id[0])
    parent_dir = "C:/Users/rithi/Desktop/Connect-main/server/Drive"
    path = os.path.join(parent_dir, directory)
    os.mkdir(path)
    parent_dir = "C:/Users/rithi/Desktop/Connect-main/server/Public"
    path = os.path.join(parent_dir, directory)
    os.mkdir(path)
    return jsonify(output)
  
        
def add_user_to_db():

    global mobile, password,mydb 
    mycursor = mydb.cursor()


    sql = "INSERT INTO user_detls (mobile,name,password) VALUES (%s, %s,%s)"
    val = (mobile,username,password)
    mycursor.execute(sql, val)
    mydb.commit()
    return 

def login(data):
    
    global mydb
    mycursor = mydb.cursor()

    mycursor.execute("select user_key,name from user_detls where mobile = '"+str(data["mobile"])+"' and password ='"+str(data["password"])+"'")
    myresult = list(mycursor.fetchall())
    if len(myresult) == 0:
        return({"status":"failed"})
    else:
        user_info = myresult
        print(user_info[0])
        return({"status":"success","user_info":list(user_info[0])})

def email_confirmation(receiver_mail, data):
    
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "rithishtemp@gmail.com"  # Enter your address
    receiver_email = receiver_mail
    message = MIMEMultipart("alternative")
    message["Subject"] = "Registration Portal"
    message["From"] = sender_email
    message["To"] = receiver_email
    password = ""
    text = """\
    """+ data["message"] +"""."""
    part1 = MIMEText(text, "plain")
    message.attach(part1)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

    output = {"status": 200}
    return "success"