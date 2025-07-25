from flask import Flask, request, jsonify
from config import Config
from extension import db, bcrypt, jwt, migrate, CORS
from routes.auth import auth_bp
from routes.loans import loan_bp
from routes.contribution import contribution_bp
from routes.contribution_schedule import schedule_bp
from mpesa import initiate_stk_push


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(loan_bp, url_prefix='/loan')
    app.register_blueprint(contribution_bp, url_prefix='/contribution')
    app.register_blueprint(schedule_bp, url_prefix='/schedule')

    # M-Pesa STK Push Endpoint
    @app.route('/mpesa/stkpush', methods=['POST'])
    def lipa_na_mpesa():
        data = request.get_json()
        phone = data.get('phone')
        amount = data.get('amount')
        response = initiate_stk_push(phone, amount)
        return jsonify(response)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
