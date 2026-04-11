from marshmallow import fields, Schema
import datetime
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import asc, desc, Index


class TokensBlocklistModels(db.Model):
    __tablename__ = 'tokenblocklist'

    id = db.Column(db.Integer, primary_key=True)
    # jti WAJIB ada — ini adalah JWT ID yang unik per token
    jti = db.Column(db.String(36), nullable=False, unique=True)
    # Tipe token: 'access' atau 'refresh'
    token_type = db.Column(db.String(10), nullable=False, default='access')
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True)
    # Kapan token direvoke
    revoked_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime)

    # Index pada jti untuk performa query — dipanggil setiap request JWT
    __table_args__ = (
        Index('ix_tokenblocklist_jti', 'jti'),
    )

    def __init__(self, data):
        self.jti = data.get('jti')
        self.token_type = data.get('token_type', 'access')
        self.member_id = data.get('member_id')
        self.revoked_at = datetime.datetime.utcnow()
        self.created_at = datetime.datetime.utcnow()

    def serialize(self):
        return {
            "id": self.id,
            "jti": self.jti,
            "token_type": self.token_type,
            "member_id": self.member_id,
            "revoked_at": str(self.revoked_at),
            "created_at": str(self.created_at)
        }

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return str(e.__dict__['orig'])

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return str(e.__dict__['orig'])

    @staticmethod
    def get_one_token(id):
        return TokensBlocklistModels.query.get(id)

    @staticmethod
    def get_tokenblock_by(jti):
        return TokensBlocklistModels.query.filter_by(jti=jti).first()

    @staticmethod
    def is_revoked(jti) -> bool:
        return TokensBlocklistModels.query.filter_by(jti=jti).first() is not None

    @staticmethod
    def revoke(jti: str, token_type: str, user_type: str = None, user_id: int = None):
        
        if TokensBlocklistModels.is_revoked(jti):
            return None

        data = {'jti': jti, 'token_type': token_type}
        field_map = {
            'member': 'member_id'
        }
        if user_type and user_id:
            field = field_map.get(user_type)
            if field:
                data[field] = user_id

        entry = TokensBlocklistModels(data)
        err = entry.save()
        if not err:
            from app.extensions import redis_client
            if redis_client:
                ttl = 86400 if token_type == 'access' else 604800
                redis_client.setex(f"blocklist:{jti}", ttl, 1)
        return err

    @staticmethod
    def get_by_user(user_type: str, user_id: int):
        field_map = {
            'member': TokensBlocklistModels.member_id
        }
        col = field_map.get(user_type)
        if col is None:
            return []
        return TokensBlocklistModels.query.filter(col == user_id).order_by(
            desc(TokensBlocklistModels.id)
        ).all()

    @staticmethod
    def get_all_token():
        return TokensBlocklistModels.query.all()

    def __repr__(self):
        return '<TokenBlocklist jti={} type={}>'.format(self.jti, self.token_type)


class TokensBlocklistSchema(Schema):
    id = fields.Int(dump_only=True)
    jti = fields.Str(required=True, allow_none=False)
    token_type = fields.Str(required=False, allow_none=True)
    member_id = fields.Int(required=False, allow_none=True)
    revoked_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
