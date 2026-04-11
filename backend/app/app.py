import os
from flask import Flask, jsonify
from flask_restful import Api
from flask_cors import CORS
from flasgger import Swagger

from app.configs.configs import app_config
from app.extensions import db, migrate
from app.security.utils import jwt

SWAGGER_CONFIG = {
    'title': 'BaliHouse API',
    'version': '1.0.0',
    'description': 'BaliHouse Leads & Members API',
    'uiversion': 3,
    'securityDefinitions': {
        'BearerAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT token. Format: **Bearer &lt;token&gt;**',
        },
        'ApiKeyAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-Key',
            'description': 'Static API key for leads endpoints',
        },
    },
    'specs_route': '/api/docs/',
}


def create_app(env=None):
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(app_config.get(env, app_config['development']))

    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    Swagger(app, config=SWAGGER_CONFIG, merge=True)

    api = Api(app, prefix='/api')

    from app.resources.leads.leadsRoutes import initialize_routes as init_leads
    init_leads(api)

    from app.resources.members.membersRoutes import initialize_routes as init_members
    init_members(api)

    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok'})

    return app