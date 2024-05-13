from flask import Flask, jsonify
import requests

 
app = Flask(__name__)

product_url = 'http://127.0.0.1:2000'
store_url = 'http://127.0.0.1:2001'


@app.route('/products', methods=['GET'])
def get_products():
    product_response = requests.get(f'{product_url}/products').json()
    
    result = []
    for res in product_response:
        store_response = requests.get(f'{store_url}/stores/{res['store_id']}').json()
        result.append({
                "id": res["id"],
                "name":res["name"],
                "description":res["description"],
                "price":res["price"],
                "store":{
                    "id":store_response["id"],
                    "name":store_response["name"],
                    "description":store_response["description"],
                    "owner":store_response["owner"],
                    "telp":store_response["telp"],
                }
            })
        
    return jsonify(result)
    


if __name__ == '__main__':
    app.run(debug=True, port=2002)