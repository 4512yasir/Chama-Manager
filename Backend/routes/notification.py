from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Notification, User
from datetime import datetime

notification_bp = Blueprint('notification', __name__)

# Send a notification to a specific user
@notification_bp.route('/send', methods=['POST'])
@jwt_required()
def send_notification():
    data = request.get_json()
    message = data.get('message')
    user_id = data.get('user_id')

    if not message or not user_id:
        return jsonify({'msg': 'Message and user_id are required'}), 400

    notification = Notification(
        message=message,
        user_id=user_id,
        sent_at=datetime.utcnow()
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({'msg': 'Notification sent successfully'}), 201

# Get logged-in user's notifications
@notification_bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_notifications():
    current_user_id = get_jwt_identity()
    notifications = Notification.query.filter_by(user_id=current_user_id).order_by(Notification.sent_at.desc()).all()

    return jsonify([
        {
            'id': note.id,
            'message': note.message,
            'sent_at': note.sent_at.strftime("%Y-%m-%d %H:%M")
        } for note in notifications
    ]), 200
