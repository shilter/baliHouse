import os
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import JWTManager

from app.models.tokenModels import TokensBlocklistModels

jwt = JWTManager()


# ── x-api-key ──────────────────────────────────────────────────────────────────

def require_api_key(f):
    """Decorator that checks the x-api-key header against API_KEY in .env."""
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('x-api-key', '')
        expected = os.getenv('api_key', '')
        if not expected or key != expected:
            return jsonify({'error': 'Unauthorized: invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated


# ── JWT ────────────────────────────────────────────────────────────────────────

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    """Called automatically on every @jwt_required() — checks blocklist."""
    jti = jwt_payload['jti']

    from app.extensions import redis_client
    if redis_client:
        if redis_client.exists(f'blocklist:{jti}'):
            return True

    return TokensBlocklistModels.get_tokenblock_by(jti=jti) is not None


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'token has been revoked'}), 401


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'token has expired'}), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'error': 'invalid token'}), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'error': 'authorization token required'}), 401