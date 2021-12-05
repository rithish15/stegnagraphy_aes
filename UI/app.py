import flask
from flask import request, jsonify
from flask_cors import CORS, cross_origin
from os import listdir
from os.path import isfile, join
import os.path, time

app = flask.Flask(__name__,template_folder='template')
app.config["DEBUG"] = True
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/', methods=['GET'])
def home():
    return '''<h1>API homepage</h1>
<p>API for Drive</p>'''

@app.route("/fetchfiles", methods=["POST", "GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def create_new_user():
    query_parameters = request.args
    uid = query_parameters.get('userid')

    mypath = "./files/" + str(uid)
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

@app.route("/upload", methods=["POST", "GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def uploadfile():
    query_parameters = request.args
    uid = query_parameters.get('userid')
    fname = query_parameters.get('fname')

    path = './files/' + uid + '/' + fname

    return jsonify({"path":path})


@app.route("/deletefile", methods=["POST", "GET"])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"])
def delete():
    query_parameters = request.args
    uid = query_parameters.get('userid')
    fname = query_parameters.get('fname')

    path = './files/' + uid + '/' + fname
    print(isfile(path))
    os.remove(path)
    return jsonify({"message":"Success"})




app.run(host='127.0.0.1', port = 5010)

