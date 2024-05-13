# store_service/store_service.py
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/store_db'
db = SQLAlchemy(app)

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    owner = db.Column(db.String(100), nullable=False)
    telp = db.Column(db.String(15), nullable=True)


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
    store = Store(
        name=name,
        description=description,
        owner=owner,
        telp=telp,
    )
    db.session.add(store)
    db.session.commit()
    
    result = {'id': store.id, 'name': store.name, 'description': store.description, 'owner': store.owner, 'telp' : store.telp }
    return jsonify(result)
    
    
if __name__ == '__main__':
    app.run(debug=True, port=2001)
