from flask import Flask
from flask_cors import CORS
from extension import db, jwt  

def create_app():
    app = Flask(__name__)

    # CORS setup for frontend
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}}, supports_credentials=True,allow_headers=['Content-Type', 'Authorization'])

    # Database and JWT config
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chama.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'super-secret-key'

    db.init_app(app)
    jwt.init_app(app)

    # Import and register blueprints
    from routes.auth import auth_bp
    from routes.loans import loans_bp
    from routes.contribution import contribution_bp
    from routes.meetings import meetings_bp
    from routes.members import members_bp
    from routes.report import reports_bp  

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(loans_bp, url_prefix='/api/loans')
    app.register_blueprint(contribution_bp, url_prefix='/api/contributions')
    app.register_blueprint(meetings_bp, url_prefix='/api/meetings')
    app.register_blueprint(members_bp, url_prefix='/api/members')
    app.register_blueprint(reports_bp, url_prefix='/api/reports') 

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
