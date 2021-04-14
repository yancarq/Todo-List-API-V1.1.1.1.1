"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User,Todo
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/todos', methods=['GET'])
def get_all_todo():
    todo = Todo.query.all()
    all_todo = list(map(lambda x: x.serialize(),todo))
    return jsonify(all_todo), 200


@app.route('/todos/<int:user_id>', methods=['GET'])
def get_user_todo(user_id):

    query = User.query.get(user_id)
    if query is None:
        return('El usuario no agregado')
    else:
        result = Todo.query.filter_by(user_id= query.id)
        todo_list = list(map(lambda x: x.serialize(), result))
        return jsonify(todo_list), 200


@app.route('/todos/<int:user_id>', methods=['POST'])
def add_new_todo(user_id):

    request_body = request.get_json() 
    if request_body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)

    label = request_body["label"]
    done = request_body["done"]

    todo = Todo(label=label,done = done,user_id = user_id) 
    db.session.add(todo)
    db.session.commit()
    
    #se retorna nuevamente la lista
    query = User.query.get(user_id)
    if query is None:
        return('El usuario no agregado'),300
    else:
        result = Todo.query.filter_by(user_id= query.id)
        todo_list = list(map(lambda x: x.serialize(), result))
        return jsonify(todo_list), 200


@app.route('/todos/<int:id_todo>', methods=['DELETE'])
def delete_todo(id_todo):

    query = Todo.query.get(id_todo)

    if query is None:
        return ({"mensaje":'La tarea no existe'}),300
    else:
        db.session.delete(query)
        db.session.commit()
        return ({"mensaje":'Tarea eliminada'}),200
    


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
