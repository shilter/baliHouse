import datetime
from app.extensions import db
from passlib.hash import bcrypt as ph


class MemberModel(db.Model):
    __tablename__ = 'member'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    token_blocklist = db.relationship('TokensBlocklistModels', backref='member', lazy=True)

    def set_password(self, raw_password):
        self.password = ph.hash(raw_password)

    def check_password(self, raw_password):
        return ph.verify(raw_password, self.password)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @staticmethod
    def get_by_email(email):
        return MemberModel.query.filter_by(email=email).first()

    @staticmethod
    def get_by_id(member_id):
        return MemberModel.query.get(member_id)