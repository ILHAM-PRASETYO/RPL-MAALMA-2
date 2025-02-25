from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.server_api import ServerApi
 
app = Flask(__name__) 
url = "mongodb+srv://ilham_templek:ilham.sukosari.templek24011@cluster-ilham.pyjie.mongodb.net/?retryWrites=true&w=majority&appName=Cluster-ilham"
 
# Create a new client and connect to the server
client = MongoClient(url, server_api=ServerApi('1'))
db = client["Data_RPL_MAALMA_2"]
collection = db["data_sensor"]
 
@app.route('/data', methods=['POST'])
def collect_data():
    data = request.json
 
    # Send to mongodb
    collection.insert_one(data)
    return jsonify({"status": "sukses", "message": "Data Masuk MongoDB"}), 201
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=6000)