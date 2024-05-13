# store_service/store_service.py
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/product_db'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Integer, nullable=False)
    store_id = db.Column(db.Integer, nullable=False)


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
    product = Product(
        name=name,
        description=description,
        price=price,
        store_id=store_id,
    )
    db.session.add(product)
    db.session.commit()
    
    result = {'id': product.id, 'name': product.name, 'description': product.description, 'price': product.price, 'store_id' : product.store_id }
    return jsonify(result)
    
    
if __name__ == '__main__':
    app.run(debug=True, port=2000)
