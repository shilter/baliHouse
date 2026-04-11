import uuid
import datetime
from app.extensions import db


class LeadStatus:
    NEW = 'new'
    CONTACTED = 'contacted'
    QUALIFIED = 'qualified'
    LOST = 'lost'

    ALL = [NEW, CONTACTED, QUALIFIED, LOST]


class LeadsModel(db.Model):
    __tablename__ = 'leads'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    budget = db.Column(db.Numeric(15, 2), nullable=True)
    status = db.Column(db.String(20), nullable=False, default=LeadStatus.NEW)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'budget': float(self.budget) if self.budget is not None else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
