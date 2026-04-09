from datetime import datetime, timezone
from app import db


class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(
        db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    make = db.Column(db.String(64), nullable=False)
    model = db.Column(db.String(64), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(32))
    license_plate = db.Column(db.String(20), index=True)
    vin = db.Column(db.String(17), unique=True, index=True)
    mileage_in = db.Column(db.Integer)  # Mileage at last check-in
    engine = db.Column(db.String(50))   # e.g. "3.5L V6"
    transmission = db.Column(db.String(20))  # auto / manual
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
    tickets = db.relationship(
        "ServiceTicket", backref="vehicle", lazy="dynamic", cascade="all, delete-orphan"
    )

    @property
    def display_name(self):
        return f"{self.year} {self.make} {self.model}"

    @property
    def active_ticket(self):
        from app.models.ticket import ServiceTicket, TicketStatus
        return self.tickets.filter(
            ServiceTicket.status.notin_([TicketStatus.COMPLETED, TicketStatus.CANCELLED])
        ).first()

    def __repr__(self):
        return f"<Vehicle {self.display_name} [{self.license_plate}]>"
