from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import jsonify
from functools import wraps

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            user = get_jwt_identity()
            if user['role'] not in roles:
                return jsonify(message="Access Denied"), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
