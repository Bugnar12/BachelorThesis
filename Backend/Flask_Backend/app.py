import os

from flask import Flask, render_template

from config.config import Config
from database import db
from jwt_auth import jwt
from routes.email_routes import email_bp
from routes.gmail_routes import gmail_bp
from routes.user_routes import user_bp

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = Flask(__name__)

# app.config['SESSION_TYPE'] = 'filesystem'
# Session(app)

app.secret_key = Config.APP_SECRET_KEY
app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY
app.config.from_object(Config)

db.init_app(app)
jwt.init_app(app)

# TODO: encapsulate all this registering in a function or something
app.register_blueprint(user_bp)
app.register_blueprint(email_bp)
app.register_blueprint(gmail_bp)

@app.route('/')
def index():
    return render_template('login_template.html')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
