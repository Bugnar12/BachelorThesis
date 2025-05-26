import os

from flask import Flask, render_template
from flask_cors import CORS
from flask_migrate import Migrate

from config.config import Config
from database import db
from jwt_auth import jwt

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = Flask(__name__)
migrate = Migrate(app, db)

CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization"])

app.secret_key = Config.APP_SECRET_KEY
app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
app.config.from_object(Config)

db.init_app(app)
jwt.init_app(app)

def register_blueprints(app):
    from routes.email_routes import email_bp
    from routes.gmail_routes import gmail_bp
    from routes.push_routes import push_bp
    from routes.user_routes import user_bp
    from routes.quiz_routes import quiz_bp

    app.register_blueprint(email_bp)
    app.register_blueprint(gmail_bp)
    app.register_blueprint(push_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(quiz_bp)

register_blueprints(app)

@app.route('/')
def index():
    return render_template('login_template.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
