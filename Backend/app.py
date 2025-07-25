from flask import Flask
from config import Config
from extension import db, bcrypt, jwt, migrate, CORS

from routes.auth import auth_bp
from routes.loans import loan_bp
from routes.contribution import contribution_bp
from routes.contribution_schedule import schedule_bp
from routes.meetings import meeting_bp
from routes.user import user_bp
from routes.Dashboard import dash_bp
from routes.system import system_bp
from routes.notification import notification_bp


# from mpesa import initiate_stk_push  # Uncomment when M-Pesa is ready

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(system_bp, url_prefix='/system')
    app.register_blueprint(dash_bp, url_prefix='/dashboard')
    app.register_blueprint(loan_bp, url_prefix='/loan')
    app.register_blueprint(contribution_bp, url_prefix='/contribution')
    app.register_blueprint(schedule_bp, url_prefix='/schedule')
    app.register_blueprint(meeting_bp, url_prefix='/meetings')
    app.register_blueprint(notification_bp, url_prefix="/api/notifications")

    # M-Pesa Integration Placeholder
    # @app.route('/mpesa/stkpush', methods=['POST'])
    # def lipa_na_mpesa():
    #     data = request.get_json()
    #     phone = data.get('phone')
    #     amount = data.get('amount')
    #     response = initiate_stk_push(phone, amount)
    #     return jsonify(response)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
