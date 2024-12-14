from sqlalchemy import text
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# configuracion de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@database-1.c58cg2s00ril.us-east-1.rds.amazonaws.com:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = 'FALSE'

db = SQLAlchemy(app)

#definicion del modelo de estudiante (modelo = tabla de base de datos es lo mismo)
class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'email': self.email
        }
    
#crear las tablas
with app.app_context():
    db.create_all()
    
    #verificar la conexion a la base de datos
    try:
        #realizar una consulta simple
        db.session.execute(text('SELECT 1'))
        print('conexion a la base de datos exitosa')
    except Exception as e:
        print(f'error al conectar: {e}')

#  Ruta para obtener usuarios
@app.route('/users', methods=['GET'])
def get_users():
    users = user.query.all()
    return jsonify([user.to_dict() for user in users])

# Ruta para crear un usuarios
@app.route('/create-user', methods=['POST'])
def create_user():
    data = request.json
    new_user = user(name = data['name'], age = data['age'], email = data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message:': 'user creation succesfully',
                    'data': new_user.to_dict()})

# Ruta para borrar todos los usuarios
@app.route('/delete-users', methods=['DELETE'])
def delete_all_users():
    db.session.query(user).delete()
    db.session.commit()
    return jsonify({'message': 'User deleted succesfully'})

# Ruta para eliminar un usuario por ID
@app.route('/delete-user/<int:user_id>', methods=['DELETE'])
def delete_user_by_id(user_id):
    user_instance = user.query.get(user_id)  # Usamos `user` con minúscula
    if user_instance:
        db.session.delete(user_instance)
        db.session.commit()
        return jsonify({'message': f'User with ID {user_id} deleted successfully'}), 200
    return jsonify({'message': 'User not found'}), 404

# Ruta para actualizar parcialmente un usuarios
@app.route('/update-user/<int:user_id>', methods=['PATCH'])
def update_one_user(user_id):
    data = request.json
    user_instance = user.query.get(user_id)
    if user_instance:
        for key, value in data.items():
            setattr(user_instance, key, value)
        db.session.commit()
        return jsonify({'message': 'Estudiante actualizado parcialmente', 'data': user_instance.to_dict()})
    return jsonify({'message': 'user not found'})