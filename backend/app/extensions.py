import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

# Redis is optional — token blocklist falls back to DB if unavailable
try:
    import redis as _redis
    _redis_url = os.getenv('REDIS_URL', '')
    redis_client = _redis.from_url(_redis_url) if _redis_url else None
except Exception:
    redis_client = None
