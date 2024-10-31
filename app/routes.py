from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from app import db
from app.models import Task, User

api_bp = Blueprint("api", __name__)  # Define the blueprint


@api_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User with this email already exists"}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid inputs"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token}), 200


@api_bp.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    priority = data.get("priority", "medium")

    new_task = Task(
        title=title, description=description, priority=priority, user_id=user_id
    )
    db.session.add(new_task)
    db.session.commit()

    return jsonify({"message": "Task created successfully"}), 201


@api_bp.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    tasks = Task.query.filter_by(user_id=user_id).all()

    tasks_data = [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status,
        }
        for task in tasks
    ]
    return jsonify(tasks_data), 200


@api_bp.route("/tasks/<int:id>", methods=["GET"])
@jwt_required()
def get_task(id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=id, user_id=user_id).first()
    if task is None:
        return jsonify({"message": "Task not found"}), 404

    task_data = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": task.status,
    }
    return jsonify(task_data), 200


@api_bp.route("/tasks/<int:id>", methods=["PUT"])
@jwt_required()
def update_task(id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=id, user_id=user_id).first()
    if task is None:
        return jsonify({"message": "Task not found"}), 404

    data = request.get_json()
    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.priority = data.get("priority", task.priority)
    task.status = data.get("status", task.status)
    db.session.commit()

    return jsonify({"message": "Task updated successfully"}), 200


@api_bp.route("/tasks/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_task(id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=id, user_id=user_id).first()
    if task is None:
        return jsonify({"message": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted successfully"}), 200


@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({"message": "Resource not found"}), 404
