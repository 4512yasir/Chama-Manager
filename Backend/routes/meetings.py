from flask import Blueprint, request, jsonify
from extension import db
from models import Meeting
from flask_jwt_extended import jwt_required
from utilis.auth import role_required
from datetime import datetime

meetings_bp = Blueprint('meetings', __name__)

@meetings_bp.route('/', methods=['GET'])
@jwt_required()
def view_meetings():
    meetings = Meeting.query.order_by(Meeting.date.desc()).all()
    return jsonify([
        {
            'id': m.id,
            'title': m.topic,
            'date': m.date.strftime('%Y-%m-%d'),
            'location': m.location,
            'minutes': m.minutes
        } for m in meetings
    ])

@meetings_bp.route('', methods=['POST'])
@jwt_required()
@role_required('admin')
def add_meeting():
    data = request.json
    required_fields = ['date', 'title', 'location']

    if not all(field in data for field in required_fields):
        return jsonify(message='Missing required fields'), 400

    try:
        parsed_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify(message='Invalid date format. Use YYYY-MM-DD.'), 400

    new_meeting = Meeting(
        date=parsed_date,
        topic=data['title'],
        location=data['location'],
        minutes=None
    )
    db.session.add(new_meeting)
    db.session.commit()
    return jsonify(message='Meeting added successfully')

@meetings_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@role_required('admin', 'secretary')
def update_minutes(id):
    meeting = Meeting.query.get(id)
    if not meeting:
        return jsonify(message='Meeting not found'), 404

    data = request.json
    if 'minutes' not in data:
        return jsonify(message='Minutes field is required'), 400

    meeting.minutes = data['minutes']
    db.session.commit()
    return jsonify(message='Meeting minutes updated successfully')

@meetings_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_meeting(id):
    meeting = Meeting.query.get(id)
    if not meeting:
        return jsonify(message='Meeting not found'), 404

    db.session.delete(meeting)
    db.session.commit()
    return jsonify(message='Meeting deleted successfully')
