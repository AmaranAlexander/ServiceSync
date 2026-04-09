from datetime import datetime, timezone
from app import db


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(
        db.Integer, db.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False, index=True
    )
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(20), nullable=False, index=True)
    email = db.Column(db.String(120), index=True)
    address = db.Column(db.String(200))
    notes = db.Column(db.Text)  # General customer notes (VIP, difficult, etc.)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    vehicles = db.relationship(
        "Vehicle", backref="owner", lazy="dynamic", cascade="all, delete-orphan"
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def vehicle_count(self):
        return self.vehicles.count()

    @property
    def all_tickets(self):
        from app.models.ticket import ServiceTicket
        vehicle_ids = [v.id for v in self.vehicles.all()]
        if not vehicle_ids:
            return []
        return ServiceTicket.query.filter(ServiceTicket.vehicle_id.in_(vehicle_ids)).all()

    def __repr__(self):
        return f"<Customer {self.full_name}>"
