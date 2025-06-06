# microservices/notification_service/app/models/notification.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

db = SQLAlchemy()


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), nullable=False)  # FK a users
    type = db.Column(
        db.Enum('appointment_reminder', 'new_appointment', 'inventory_alert', 'general', name='notification_type_enum'),
        nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Campos adicionales para tracking de envío
    email_sent = db.Column(db.Boolean, default=False)
    sms_sent = db.Column(db.Boolean, default=False)
    email_sent_at = db.Column(db.DateTime)
    sms_sent_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'is_read': self.is_read,
            'email_sent': self.email_sent,
            'sms_sent': self.sms_sent,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def get_by_user(cls, user_id, unread_only=False):
        # Convertir string a UUID si es necesario
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        query = cls.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def mark_as_read(cls, notification_id, user_id):
        # Convertir strings a UUID si es necesario
        if isinstance(notification_id, str):
            notification_id = uuid.UUID(notification_id)
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        notification = cls.query.filter_by(id=notification_id, user_id=user_id).first()
        if notification:
            notification.is_read = True
            db.session.commit()
            return notification
        return None

    @classmethod
    def create_notification(cls, user_id, notification_type, title, message):
        # Convertir string a UUID si es necesario
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        notification = cls(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message
        )
        db.session.add(notification)
        db.session.commit()
        return notification