import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
from AES_module import AES
import numpy as np
from PIL import Image
from Convert import converter
from authentication_api import new_user,login
import ast
from random import randint
from urllib.request import urlopen
import json
from os import listdir
from os.path import isfile, join
import os.path, time
import requests
import shutil

#flask Config
app = flask.Flask(__name__,template_folder='template')
app.config["DEBUG"] = True
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
ecc_private = ""
aes_key_d = ""
ecc_public_d = ""
C1_aesKey_d = ""
C2_aesKey_d = ""
C1_multimedia_d = ""
C2_multimedia_d = ""





@app.route("/new_user", methods=["POST", "GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def create_new_user():
    data = request.get_json()
    print(data)
    return new_user(data)

@app.route("/login", methods=["POST", "GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def logging_in():
    data = request.get_json()
    print(data)
    return login(data)
    
# 3
@app.route("/save_stegno_file", methods=["POST", "GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def stegno_save():
   from werkzeug.datastructures import FileStorage
   FileStorage(request.stream).save('./downloads/img.png')
   return 'OK', 200
   
 

@app.route("/save_file", methods=["POST", "GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def decrypt():
   data = request.get_json()
   print(data)
   Uid = data["User_id"]
   file_name =  r".\Drive\\"+Uid+"\\"+data["File_name"]


   stegano_message = Decode('C:/Users/rithi/Desktop/Connect-main/server/downloads/img.png')
   data_to_decrypt =  stegano_message[:-2]
   aes_key_d = int(stegano_message[-2:])
   
 
   # Decryption
   clean_data_list_d = converter.makeListFromString(data_to_decrypt)
   aes_obj = AES.AES(int(aes_key_d))
   decrypted_multimedia_d = aes_obj.decryptBigData(clean_data_list_d)
   converter.base64ToFile(decrypted_multimedia_d, str(file_name))
   return ({"status":"success"})
 
def Decode(src):
 
   img = Image.open(src, 'r')
   array = np.array(list(img.getdata()))
 
   if img.mode == 'RGB':
       n = 3
   elif img.mode == 'RGBA':
       n = 4
   total_pixels = array.size//n
 
   hidden_bits = ""
   for p in range(total_pixels):
       for q in range(0, 3):
           hidden_bits += (bin(array[p][q])[2:][-1])
 
   hidden_bits = [hidden_bits[i:i+8] for i in range(0, len(hidden_bits), 8)]
 
   message = ""
   for i in range(len(hidden_bits)):
       if message[-5:] == "$#$#$":
           break
       else:
           message += chr(int(hidden_bits[i], 2))
   if message[-5:] == "$#$#$":
       return message[:-5]
      
   else:
       print("No Hidden Message Found")
       exit()


def encryption_d(uid,file_name):
   file = file_name
   multimedia_data = converter.fileToBase64(str(file))
   aes_key = randint(10,99)
   aes = AES.AES(int(aes_key))
   encrypted_multimedia = aes.encryptBigData(multimedia_data)
   encrypted = converter.makeSingleString(encrypted_multimedia)
 
   data_to_encrypt = encrypted
   Encode_d('./uploads/img_d.png',data_to_encrypt,'./downloads/img_d.png',aes_key)
   with open('./downloads/img_d.png', 'rb') as f:
    requests.post('http://192.168.0.103:8001/save_stegno_file_d', data=f)
   
   url = 'http://192.168.0.103:8001/save_file_d'
   data = {"File_name" :file_name,"User_id" :uid}  
   r = requests.post(url,verify=False, json=data)
   while True:
       if (r.status_code == 200):
          print("Successfully uploaded file")
          return 100;

def Encode_d(src, message, dest,aes_key):
     
   img = Image.open(src, 'r')
   width, height = img.size
   array = np.array(list(img.getdata()))
 
   if img.mode == 'RGB':
       n = 3
   elif img.mode == 'RGBA':
       n = 4
   total_pixels = array.size//n
   message += str(aes_key)+"$#$#$"  
   b_message = ''.join([format(ord(i), "08b") for i in message])
   req_pixels = len(b_message)
 
   if req_pixels > total_pixels:
       print("ERROR: Need larger file size")
 
   else:
       index=0
       for p in range(total_pixels):
           for q in range(0, 3):
               if index < req_pixels:
                   array[p][q] = int(bin(array[p][q])[2:9] + b_message[index], 2)
                   index += 1
 
       array=array.reshape(height, width, n)
       enc_img = Image.fromarray(array.astype('uint8'), img.mode)
       enc_img.save(dest)
       print("Image Encoded Successfully")
       return
 

@app.route("/download", methods=["POST", "GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def file_download():
    query_parameters = request.args
    uid = query_parameters.get('userid')
    file_name = query_parameters.get('fname')
    aes_key_d = randint(10,99)
    encryption_d(uid, ".\Drive\\"+uid+"\\"+file_name)
    return "success"

@app.route("/fetchfiles", methods=["POST", "GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def fetch_files():
    query_parameters = request.args
    uid = query_parameters.get('userid')

    mypath = "./Drive/" + str(uid)
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    res = []
    
    for i in onlyfiles:
        tmp = []
        tmp.append(i)
        time1 = time.ctime(os.path.getctime(mypath + "/" + i))
        print(time1)
        tmp.append(time1)
        tmp.append(i.split('.')[1])
        res.append(tmp)
    return jsonify({"res": res})

@app.route("/fetchallpublicfiles", methods=["POST", "GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def fetch_public_all_files():
    query_parameters = request.args
    uid = query_parameters.get('userid')

    root = "./Public/" 
    onlyfiles = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            print(os.path.join(path, name))
            onlyfiles.append(os.path.join(path, name))
    res = []
    
    for i in onlyfiles:
        tmp = []
        name =  i.split('\\')[1]
        tmp.append(name)
        time1 = time.ctime(os.path.getctime(i))
        print(time1)
        tmp.append(time1)
        tmp.append(i.split('.')[2])
        user = i[i.rfind('/')+1:i.rfind('\\')] 
        tmp.append(user)
        res.append(tmp)
    print(res)
    return jsonify({"res": res})


@app.route("/download_public_file", methods=["POST", "GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def public_file_download():
    query_parameters = request.args
    uid = query_parameters.get('userid')
    file_name = query_parameters.get('fname')
    aes_key_d = randint(10,99)
    encryption_d(uid, ".\Public\\"+uid+"\\"+file_name)
    return "success"


@app.route("/deletefile", methods=["POST", "GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def delete():
    query_parameters = request.args
    uid = query_parameters.get('userid')
    fname = query_parameters.get('fname')
    path = './Drive/' + uid + '/' + fname
    print(isfile(path))
    os.remove(path)
    return jsonify({"message":"Success"})

@app.route("/make_public", methods=["POST","GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def makePublic():
    query_parameters = request.args
    uid = query_parameters.get('userid')
    fname = query_parameters.get('fname')
    print(uid,fname)
    src_path = 'C:/Users/rithi/Desktop/Connect-main/server/Drive/' + uid + '/' + fname
    dst_path = 'C:/Users/rithi/Desktop/Connect-main/server/Public/' + uid + '/' + fname
    print(src_path,dst_path)
    shutil.move(src_path, dst_path)
    status_code = flask.Response(status=200)
    return status_code


@app.route("/delete_public_file", methods=["POST", "GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def delete_public():
    query_parameters = request.args
    uid = query_parameters.get('userid')
    fname = query_parameters.get('fname')
    path = './Public/' + uid + '/' + fname
    print(isfile(path))
    os.remove(path)
    return jsonify({"message":"Success"})

app.run(host='192.168.0.103', port = 8002)