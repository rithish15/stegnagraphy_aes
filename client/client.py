import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
from AES_module import AES
import numpy as np
from PIL import Image
from Convert import converter
import ast
from random import randint
import requests
from urllib.request import urlopen
import json
import time

#flask Config
app = flask.Flask(__name__,template_folder='templates')
app.config["DEBUG"] = True
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


# 2
def encryption(uid,file_name):
   file = "./uploads/Files/"+file_name
   multimedia_data = converter.fileToBase64(str(file))
   aes_key = randint(10,99)
   aes = AES.AES(int(aes_key))
   encrypted_multimedia = aes.encryptBigData(multimedia_data)
   encrypted = converter.makeSingleString(encrypted_multimedia)
 
   data_to_encrypt = encrypted
   Encode('./uploads/img.png',data_to_encrypt,'./download/img.png',aes_key)
   with open('./download/img.png', 'rb') as f:
    requests.post('http://192.168.0.103:8002/save_stegno_file', data=f)
   
   url = 'http://192.168.0.103:8002/save_file'
   data = {"File_name" :file_name,"User_id" :uid}  
   r = requests.post(url,verify=False, json=data)
   while True:
       if (r.status_code == 200):
          print("Successfully uploaded file")
          return 100;
   
 
def Encode(src, message, dest,aes_key):
 
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
 
 
@app.route("/upload", methods=["POST", "GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def file_upload():
   query_parameters = request.args
   uid = query_parameters.get('userid')
   file_name = query_parameters.get('fname')
   print(uid,file_name)
   out = encryption(uid,file_name)
   if out == 100:
    return "success"


#download

# 3
@app.route("/download_file", methods=["POST", "GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def decrypt():
    data = request.get_json()
    Uid = data["User_id"]
    file_name =  r".\download\\"+data["File_name"]

    
    return ({"status":"success"})

@app.route("/save_stegno_file_d", methods=["POST", "GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def stegno_save():
   from werkzeug.datastructures import FileStorage
   FileStorage(request.stream).save('./download/img_d.png')
   return 'OK', 200
   
 

@app.route("/save_file_d", methods=["POST", "GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def decrypt_d():
   data = request.get_json()
   print(data)
   file_name = data["File_name"]
   Uid = data["User_id"]
   file_name =  r".\download\Files\\"+  file_name[file_name.rfind('\\')+1:]
 

   stegano_message = Decode('C:/Users/rithi/Desktop/Connect-main/client/download/img_d.png')
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


if __name__ == "__main__":
    app.run(host='192.168.0.103', port = 8001)
