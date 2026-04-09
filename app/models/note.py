from datetime import datetime, timezone
from app import db


class ServiceNote(db.Model):
    __tablename__ = "service_notes"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("service_tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL")
    )
    body = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=True, nullable=False)  # internal staff note vs customer-facing
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self):
        return f"<ServiceNote ticket={self.ticket_id} by={self.author_id}>"
