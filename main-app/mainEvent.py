from flask import Flask, jsonify
import requests
import pika

app = Flask(__name__)

store_url = 'http://127.0.0.1:2001'


def consume_message():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='product_created_queue')

    def callback(ch, method, properties, body):
        product = requests.get(f'http://127.0.0.1:2000/products/{body.decode()}').json()
        store_response = requests.get(f'{store_url}/stores/{product['store_id']}').json()
        result = {
            "id": product["id"],
            "name": product["name"],
            "description": product["description"],
            "price": product["price"],
            "store": {
                "id": store_response["id"],
                "name": store_response["name"],
                "description": store_response["description"],
                "owner": store_response["owner"],
                "telp": store_response["telp"],
            }
        }
        print("Product details:", result)
    
    channel.basic_consume(queue='product_created_queue', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


@app.route('/products', methods=['GET'])
def get_products():
    product_response = requests.get('http://127.0.0.1:2000/products').json()

    result = []
    for res in product_response:
        store_response = requests.get(f'{store_url}/stores/{res["store_id"]}').json()
        result.append({
            "id": res["id"],
            "name": res["name"],
            "description": res["description"],
            "price": res["price"],
            "store": {
                "id": store_response["id"],
                "name": store_response["name"],
                "description": store_response["description"],
                "owner": store_response["owner"],
                "telp": store_response["telp"],
            }
        })

    return jsonify(result)


if __name__ == '__main__':
    consume_message()
    app.run(debug=True, port=2002)
