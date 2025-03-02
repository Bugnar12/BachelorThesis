from database import db

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(200), nullable=False)
    user_email = db.Column(db.String(200), unique=True)
    user_password = db.Column(db.String(200), unique=True, nullable=False)

    def __init__(self, user_name, user_email, user_password):
        self.user_name = user_name
        self.user_email = user_email
        self.user_password = user_password

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "user_email": self.user_email,
        }

    def from_dict(self, data):
        for field in ["user_name", "user_email", "user_password"]:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return "User: {}".format(self.user_name)