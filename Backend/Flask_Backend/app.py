from flask import Flask
from config.config import Config
from database import db
from routes.user_routes import user_bp
from utils.logs import get_logger

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
app.register_blueprint(user_bp)


with app.app_context():
    db.create_all()

# ✅ Run the App
if __name__ == "__main__":
    app.run()
