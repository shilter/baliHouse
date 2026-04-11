import os
import re
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_

from app.extensions import db
from app.models.memberModels import MemberModel

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

DEFAULT_PAGE = int(os.getenv('page', 1))
DEFAULT_PER_PAGE = int(os.getenv('per_page', 10))


class MembersListResource(Resource):
    @jwt_required()
    def get(self):
        """
        List all members with pagination and search
        ---
        tags:
          - Members
        security:
          - BearerAuth: []
        parameters:
          - in: query
            name: q
            type: string
            description: Search by name or email (partial, case-insensitive)
          - in: query
            name: name
            type: string
            description: Filter by name
          - in: query
            name: email
            type: string
            description: Filter by email
          - in: query
            name: page
            type: integer
            default: 1
          - in: query
            name: per_page
            type: integer
            default: 10
        responses:
          200:
            description: Paginated list of members
          401:
            description: Missing or invalid token
        """
        q = request.args.get('q', '').strip()
        name_q = request.args.get('name', '').strip()
        email_q = request.args.get('email', '').strip()

        try:
            page = int(request.args.get('page', DEFAULT_PAGE))
            per_page = min(int(request.args.get('per_page', DEFAULT_PER_PAGE)), 100)
        except ValueError:
            return {'error': 'page and per_page must be integers'}, 400

        query = MemberModel.query

        if q:
            like = f'%{q}%'
            query = query.filter(
                or_(
                    MemberModel.name.ilike(like),
                    MemberModel.email.ilike(like),
                )
            )
        if name_q:
            query = query.filter(MemberModel.name.ilike(f'%{name_q}%'))
        if email_q:
            query = query.filter(MemberModel.email.ilike(f'%{email_q}%'))

        query = query.order_by(MemberModel.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'data': [m.to_dict() for m in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
            },
        }, 200


class MembersDetailResource(Resource):
    @jwt_required()
    def get(self, member_id):
        """
        Get a member by ID
        ---
        tags:
          - Members
        security:
          - BearerAuth: []
        parameters:
          - in: path
            name: member_id
            type: integer
            required: true
        responses:
          200:
            description: Member data
          401:
            description: Missing or invalid token
          404:
            description: Member not found
        """
        member = MemberModel.get_by_id(member_id)
        if not member:
            return {'error': 'Member not found'}, 404
        return member.to_dict(), 200

    @jwt_required()
    def patch(self, member_id):
        """
        Update a member's profile (own profile only)
        ---
        tags:
          - Members
        security:
          - BearerAuth: []
        parameters:
          - in: path
            name: member_id
            type: integer
            required: true
          - in: body
            name: body
            schema:
              type: object
              properties:
                name:
                  type: string
                  example: Jane Doe
                email:
                  type: string
                  example: jane@example.com
                password:
                  type: string
                  example: newpassword123
        responses:
          200:
            description: Updated member data
          400:
            description: Validation error
          401:
            description: Missing or invalid token
          403:
            description: Cannot update another member's profile
          404:
            description: Member not found
          409:
            description: Email already in use
        """
        current_id = int(get_jwt_identity())
        if current_id != member_id:
            return {'error': 'You can only update your own profile'}, 403

        member = MemberModel.get_by_id(member_id)
        if not member:
            return {'error': 'Member not found'}, 404

        data = request.get_json(silent=True)
        if not data:
            return {'error': 'Request body must be JSON'}, 400

        if 'name' in data:
            name = (data['name'] or '').strip()
            if not name:
                return {'error': 'name cannot be empty'}, 400
            member.name = name

        if 'email' in data:
            email = (data['email'] or '').strip().lower()
            if not EMAIL_RE.match(email):
                return {'error': 'email format is invalid'}, 400
            existing = MemberModel.get_by_email(email)
            if existing and existing.id != member_id:
                return {'error': 'email already in use'}, 409
            member.email = email

        if 'password' in data:
            password = data['password'] or ''
            if len(password) < 6:
                return {'error': 'password must be at least 6 characters'}, 400
            member.set_password(password)

        db.session.commit()
        return member.to_dict(), 200

    @jwt_required()
    def delete(self, member_id):
        """
        Delete a member account (own account only)
        ---
        tags:
          - Members
        security:
          - BearerAuth: []
        parameters:
          - in: path
            name: member_id
            type: integer
            required: true
        responses:
          204:
            description: Member deleted
          401:
            description: Missing or invalid token
          403:
            description: Cannot delete another member's account
          404:
            description: Member not found
        """
        current_id = int(get_jwt_identity())
        if current_id != member_id:
            return {'error': 'You can only delete your own account'}, 403

        member = MemberModel.get_by_id(member_id)
        if not member:
            return {'error': 'Member not found'}, 404

        db.session.delete(member)
        db.session.commit()
        return '', 204