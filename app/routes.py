from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from . import db, bcrypt
from .models import User, Contact
from . import create_app

app = create_app()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    password = data['password']
    
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "User already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created", "user": {"email": new_user.email}}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    
    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"msg": "Bad email or password"}), 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

@app.route('/contacts', methods=['POST'])
@jwt_required()
def create_contact():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    new_contact = Contact(name=data['name'], phone=data['phone'], user_id=current_user_id)
    db.session.add(new_contact)
    db.session.commit()
    return jsonify({"msg": "Contact created", "contact": {"name": new_contact.name, "phone": new_contact.phone}}), 201

@app.route('/contacts', methods=['GET'])
@jwt_required()
def get_contacts():
    current_user_id = get_jwt_identity()
    contacts = Contact.query.filter_by(user_id=current_user_id).all()
    contacts_list = [{"id": contact.id, "name": contact.name, "phone": contact.phone} for contact in contacts]
    return jsonify(contacts=contacts_list), 200

@app.route('/contacts/<int:contact_id>', methods=['DELETE'])
@jwt_required()
def delete_contact(contact_id):
    current_user_id = get_jwt_identity()
    contact = Contact.query.filter_by(id=contact_id, user_id=current_user_id).first()
    if not contact:
        return jsonify({"msg": "Contact not found"}), 404

    db.session.delete(contact)
    db.session.commit()
    return jsonify({"msg": "Contact deleted"}), 200
