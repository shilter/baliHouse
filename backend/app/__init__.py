from .app import create_app

def create_app_default():
    import os
    env_name = os.getenv("FLASK_ENV", "development")
    return create_app(env_name)