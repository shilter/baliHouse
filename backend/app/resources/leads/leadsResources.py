import re
from flask import request, jsonify
from flask_restful import Resource

from app.extensions import db
from app.models.leadsModel import LeadsModel, LeadStatus
from app.security.utils import require_api_key


EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


class LeadsListResource(Resource):
    @require_api_key
    def get(self):
        """
        List all leads
        ---
        tags:
          - Leads
        security:
          - ApiKeyAuth: []
        parameters:
          - in: query
            name: status
            type: string
            enum: [new, contacted, qualified, lost]
            description: Filter leads by status
        responses:
          200:
            description: List of leads
          400:
            description: Invalid status value
          401:
            description: Missing or invalid API key
        """
        status_filter = request.args.get('status')
        query = LeadsModel.query.order_by(LeadsModel.created_at.desc())
        if status_filter:
            if status_filter not in LeadStatus.ALL:
                return {'error': f'Invalid status. Must be one of: {", ".join(LeadStatus.ALL)}'}, 400
            query = query.filter_by(status=status_filter)
        leads = query.all()
        return [lead.to_dict() for lead in leads], 200

    @require_api_key
    def post(self):
        """
        Create a new lead
        ---
        tags:
          - Leads
        security:
          - ApiKeyAuth: []
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required: [name, email]
              properties:
                name:
                  type: string
                  example: Alice Smith
                email:
                  type: string
                  example: alice@example.com
                phone:
                  type: string
                  example: "+6281234567890"
                budget:
                  type: number
                  example: 500000000
                notes:
                  type: string
                  example: Interested in villa near Seminyak
        responses:
          201:
            description: Lead created
          400:
            description: Validation error
          401:
            description: Missing or invalid API key
        """
        data = request.get_json(silent=True)
        if not data:
            return {'error': 'Request body must be JSON'}, 400

        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip()

        if not name:
            return {'error': 'name is required'}, 400
        if not email:
            return {'error': 'email is required'}, 400
        if not EMAIL_RE.match(email):
            return {'error': 'email format is invalid'}, 400

        budget = data.get('budget')
        if budget is not None:
            try:
                budget = float(budget)
                if budget < 0:
                    return {'error': 'budget must be a non-negative number'}, 400
            except (TypeError, ValueError):
                return {'error': 'budget must be a number'}, 400

        lead = LeadsModel(
            name=name,
            email=email,
            phone=(data.get('phone') or '').strip() or None,
            budget=budget,
            status=LeadStatus.NEW,
            notes=(data.get('notes') or '').strip() or None,
        )
        db.session.add(lead)
        db.session.commit()
        return lead.to_dict(), 201


class LeadsDetailResource(Resource):
    @require_api_key
    def patch(self, lead_id):
        """
        Update a lead's status or notes
        ---
        tags:
          - Leads
        security:
          - ApiKeyAuth: []
        parameters:
          - in: path
            name: lead_id
            type: string
            required: true
          - in: body
            name: body
            schema:
              type: object
              properties:
                status:
                  type: string
                  enum: [new, contacted, qualified, lost]
                notes:
                  type: string
                  example: Follow up scheduled
        responses:
          200:
            description: Updated lead data
          400:
            description: Validation error
          401:
            description: Missing or invalid API key
          404:
            description: Lead not found
        """
        lead = LeadsModel.query.get(lead_id)
        if not lead:
            return {'error': 'Lead not found'}, 404

        data = request.get_json(silent=True)
        if not data:
            return {'error': 'Request body must be JSON'}, 400

        if 'status' in data:
            if data['status'] not in LeadStatus.ALL:
                return {'error': f'Invalid status. Must be one of: {", ".join(LeadStatus.ALL)}'}, 400
            lead.status = data['status']

        if 'notes' in data:
            lead.notes = (data['notes'] or '').strip() or None

        db.session.commit()
        return lead.to_dict(), 200

    @require_api_key
    def delete(self, lead_id):
        """
        Delete a lead
        ---
        tags:
          - Leads
        security:
          - ApiKeyAuth: []
        parameters:
          - in: path
            name: lead_id
            type: string
            required: true
        responses:
          204:
            description: Lead deleted
          401:
            description: Missing or invalid API key
          404:
            description: Lead not found
        """
        lead = LeadsModel.query.get(lead_id)
        if not lead:
            return {'error': 'Lead not found'}, 404

        db.session.delete(lead)
        db.session.commit()
        return '', 204
