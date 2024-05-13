from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import pika
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/product_db'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Integer, nullable=False)
    store_id = db.Column(db.Integer, nullable=False)

def publish_message(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='product_queue')
    channel.basic_publish(exchange='', routing_key='product_queue', body=message)
    connection.close()

def consume_message():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='product_queue')
    
    def callback(ch, method, properties, body):
        message = json.loads(body)
        product = Product(
            name=message['name'],
            description=message['description'],
            price=message['price'],
            store_id=message['store_id'],
        )
        db.session.add(product)
        db.session.commit()
        print("Product created:", product.id)
    
    channel.basic_consume(queue='product_queue', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    result = [{'id': product.id, 'name': product.name, 'description': product.description, 'price': product.price, 'store_id' : product.store_id } for product in products]
    return jsonify(result)

@app.route('/products/<int:id>')
def get_product_by_id(id):
    product = Product.query.get(id)
    if product:
        result = {'id': product.id, 'name': product.name, 'description': product.description, 'price': product.price, 'store_id' : product.store_id }
        return jsonify(result)
    else:
        return jsonify({"error":"Data not found"}), 404

@app.route('/products', methods=['POST'])
def create_product():
    name = request.json['name']
    description = request.json['description']
    price = request.json['price']
    store_id = request.json['store_id']
    message = json.dumps({
        'name': name,
        'description': description,
        'price': price,
        'store_id': store_id
    })
    publish_message(message)
    return jsonify({"message": "Product creation request sent"}), 202

if __name__ == '__main__':
    app.run(debug=True, port=2000)
