from database import db

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(200), nullable=False)
    user_email = db.Column(db.String(200), unique=True)
    user_password = db.Column(db.String(50), unique=True, nullable=False)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "user_name": self.user_name,
            "user_email": self.user_email,
            "user_password": self.user_password
        }

    def from_dict(self, data):
        for field in ["user_name", "user_email", "user_password"]:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return "User: {}".format(self.user_name)