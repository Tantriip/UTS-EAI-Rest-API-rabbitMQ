from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import pika
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/store_db'
db = SQLAlchemy(app)

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    owner = db.Column(db.String(100), nullable=False)
    telp = db.Column(db.String(15), nullable=True)

def publish_message(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='store_queue')
    channel.basic_publish(exchange='', routing_key='store_queue', body=message)
    connection.close()

def consume_message():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='store_queue')
    
    def callback(ch, method, properties, body):
        message = json.loads(body)
        store = Store(
            name=message['name'],
            description=message['description'],
            owner=message['owner'],
            telp=message['telp'],
        )
        db.session.add(store)
        db.session.commit()
        print("Store created:", store.id)
    
    channel.basic_consume(queue='store_queue', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

@app.route('/stores', methods=['GET'])
def get_stores():
    stores = Store.query.all()
    result = [{'id': store.id, 'name': store.name, 'description': store.description, 'owner': store.owner, 'telp' : store.telp } for store in stores]
    return jsonify(result)

@app.route('/stores/<int:id>')
def get_store_by_id(id):
    store = Store.query.get(id)
    if store:
        result = {'id': store.id, 'name': store.name, 'description': store.description, 'owner': store.owner, 'telp' : store.telp }
        return jsonify(result)
    else:
        return jsonify({"error":"Data not found"}), 404

@app.route('/stores', methods=['POST'])
def create_store():
    name = request.json['name']
    description = request.json['description']
    owner = request.json['owner']
    telp = request.json['telp']
    message = json.dumps({
        'name': name,
        'description': description,
        'owner': owner,
        'telp': telp
    })
    publish_message(message)
    return jsonify({"message": "Store creation request sent"}), 202

if __name__ == '__main__':
    app.run(debug=True, port=2001)
