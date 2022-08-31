import threading
from flask import Flask, request, jsonify
import json
from flask_cors import CORS
from time import sleep

from BookingTaxi import BookingTaxi
from Register import Register
from Travel import Travel
from Update import Update

app = Flask(__name__)
cors = CORS(app)

@app.route('/register/<string:user>', methods=['POST'])
def register(user):
    data = json.loads(request.data.decode('utf-8'))
    if user == "taxis":
        taxi_user = Register(user)
        message = taxi_user.insertTaxis(data)
    elif user == "customers":
        customer_user = Register(user)
        message = customer_user.insertCutomers(data)
    else:
        message = {'statusCode':400,'msg':"Error: Wrong request"}
    return jsonify(message), message['statusCode']

@app.route('/update/<string:user>', methods=['GET'])
def update(user):
    if user == 'taxis':
        message = Update().updateTaxisLocation()
    elif user == 'customers':
        message = Update().updateCustomerLocation()
    else:
        message = {'statusCode':400,'msg':"Error: Wrong request"}
    return message['msg'], message['statusCode']

@app.route("/findtaxi", methods=['POST'])
def findTaxi():
    data = json.loads(request.data.decode('utf-8'))
    taxi = BookingTaxi()
    taxiList = taxi.findNearestTaxi(data['location'],data['type'])
    notification_res = taxi.setNotification(data,taxiList)
    if notification_res:
        message = {"statusCode":200,"msg":taxiList}
    else:
        message = {"statusCode":400,"msg":'Error: cannot request taxi'}
    return jsonify(message), message['statusCode']

@app.route("/notification/<int:id>", methods=['GET'])
def getNotification(id):
    taxi = BookingTaxi()
    notification = taxi.getNotification(id)
    message = {"statusCode":200,"msg":notification}
    return jsonify(message['msg']), message['statusCode']

@app.route("/accept", methods=['POST'])
def requestNotification():
    data = json.loads(request.data.decode('utf-8'))
    taxi = BookingTaxi()
    request_res = taxi.deleteBooking(data)
    message = {"statusCode":200,"msg":request_res}
    return jsonify(message['msg']), message['statusCode']

@app.route("/starttrip", methods=['POST'])
def startTrip():
    data = json.loads(request.data.decode('utf-8'))
    def long_running_task():
        print("Starting long task")
        print("Your params:", data)
        message = Travel().startTrip(data)
        print(message['msg'])
        
    thread = threading.Thread(target=long_running_task)
    thread.start()

    message = {"statusCode":200,"msg": "Have a safe tarvel ahead"}
    return jsonify(message['msg']), message['statusCode']

@app.route('/tripupdate/<int:id>', methods=['GET'])
def tripupdate(id):
    message = Update().updateTripData(id)
    return jsonify(message), message['statusCode']

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
