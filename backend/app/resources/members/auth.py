import os
import re
from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from app.extensions import db
from app.models.memberModels import MemberModel
from app.models.tokenModels import TokensBlocklistModels

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


class RegisterResource(Resource):
    def post(self):
        """
        Register a new member
        ---
        tags:
          - Auth
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [name, email, password]
              properties:
                name:
                  type: string
                  example: John Doe
                email:
                  type: string
                  example: john@example.com
                password:
                  type: string
                  example: secret123
        responses:
          201:
            description: Member created
          400:
            description: Validation error
          409:
            description: Email already registered
        """
        data = request.get_json(silent=True)
        if not data:
            return {'error': 'Request body must be JSON'}, 400

        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''

        if not name:
            return {'error': 'name is required'}, 400
        if not email:
            return {'error': 'email is required'}, 400
        if not EMAIL_RE.match(email):
            return {'error': 'email format is invalid'}, 400
        if len(password) < 6:
            return {'error': 'password must be at least 6 characters'}, 400

        if MemberModel.get_by_email(email):
            return {'error': 'email already registered'}, 409

        member = MemberModel(name=name, email=email)
        member.set_password(password)
        db.session.add(member)
        db.session.commit()

        return member.to_dict(), 201


class LoginResource(Resource):
    def post(self):
        """
        Login and get JWT tokens
        ---
        tags:
          - Auth
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [email, password]
              properties:
                email:
                  type: string
                  example: john@example.com
                password:
                  type: string
                  example: secret123
        responses:
          200:
            description: Login successful, returns access_token and refresh_token
          400:
            description: Missing fields
          401:
            description: Invalid credentials
        """
        data = request.get_json(silent=True)
        if not data:
            return {'error': 'Request body must be JSON'}, 400

        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''

        if not email or not password:
            return {'error': 'email and password are required'}, 400

        member = MemberModel.get_by_email(email)
        if not member or not member.check_password(password):
            return {'error': 'Invalid email or password'}, 401

        access_token = create_access_token(identity=str(member.id))
        refresh_token = create_refresh_token(identity=str(member.id))

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'api_key': os.getenv('api_key', ''),
            'member': member.to_dict(),
        }, 200


class LogoutResource(Resource):
    @jwt_required()
    def delete(self):
        """
        Logout (revoke current JWT token)
        ---
        tags:
          - Auth
        security:
          - BearerAuth: []
        responses:
          200:
            description: Successfully logged out
          401:
            description: Missing or invalid token
          500:
            description: Could not revoke token
        """
        claims = get_jwt()
        jti = claims['jti']
        token_type = claims['type']
        member_id = int(get_jwt_identity())

        err = TokensBlocklistModels.revoke(
            jti=jti,
            token_type=token_type,
            user_type='member',
            user_id=member_id,
        )
        if err:
            return {'error': 'Could not revoke token'}, 500

        return {'message': 'Successfully logged out'}, 200


class MeResource(Resource):
    @jwt_required()
    def get(self):
        """
        Get current logged-in member profile
        ---
        tags:
          - Auth
        security:
          - BearerAuth: []
        responses:
          200:
            description: Current member data
          401:
            description: Missing or invalid token
          404:
            description: Member not found
        """
        member_id = int(get_jwt_identity())
        member = MemberModel.get_by_id(member_id)
        if not member:
            return {'error': 'Member not found'}, 404
        return member.to_dict(), 200


class RefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        """
        Refresh access token using refresh token
        ---
        tags:
          - Auth
        security:
          - BearerAuth: []
        responses:
          200:
            description: New access token
          401:
            description: Missing or invalid refresh token
        """
        member_id = get_jwt_identity()
        new_access_token = create_access_token(identity=member_id)
        return {'access_token': new_access_token}, 200