# microservices/appointment_service/app/models/appointment.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, date, time

db = SQLAlchemy()


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pet_id = db.Column(UUID(as_uuid=True), nullable=False)  # FK a pets (en medical service)
    veterinarian_id = db.Column(UUID(as_uuid=True), nullable=False)  # FK a users
    client_id = db.Column(UUID(as_uuid=True), nullable=False)  # FK a users
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.Enum('scheduled', 'confirmed', 'completed', 'cancelled', name='appointment_status_enum'),
                       default='scheduled')
    reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'pet_id': str(self.pet_id),
            'veterinarian_id': str(self.veterinarian_id),
            'client_id': str(self.client_id),
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_time': self.appointment_time.strftime('%H:%M') if self.appointment_time else None,
            'status': self.status,
            'reason': self.reason,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_by_veterinarian(cls, vet_id, start_date=None, end_date=None):
        # Convertir string a UUID si es necesario
        if isinstance(vet_id, str):
            vet_id = uuid.UUID(vet_id)

        query = cls.query.filter_by(veterinarian_id=vet_id)
        if start_date:
            query = query.filter(cls.appointment_date >= start_date)
        if end_date:
            query = query.filter(cls.appointment_date <= end_date)
        return query.order_by(cls.appointment_date, cls.appointment_time).all()

    @classmethod
    def get_by_client(cls, client_id, status=None):
        # Convertir string a UUID si es necesario
        if isinstance(client_id, str):
            client_id = uuid.UUID(client_id)

        query = cls.query.filter_by(client_id=client_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(cls.appointment_date.desc(), cls.appointment_time.desc()).all()

    @classmethod
    def check_availability(cls, vet_id, appointment_date, appointment_time):
        """Verificar si un horario está disponible"""
        # Convertir string a UUID si es necesario
        if isinstance(vet_id, str):
            vet_id = uuid.UUID(vet_id)

        existing = cls.query.filter_by(
            veterinarian_id=vet_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status='scheduled'
        ).first()
        return existing is None