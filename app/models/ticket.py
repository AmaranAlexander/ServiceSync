from datetime import datetime, timezone
from app import db


class TicketStatus:
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    READY_FOR_PICKUP = "ready_for_pickup"
    CANCELLED = "cancelled"

    ALL = [WAITING, IN_PROGRESS, ON_HOLD, COMPLETED, READY_FOR_PICKUP, CANCELLED]
    ACTIVE = [WAITING, IN_PROGRESS, ON_HOLD]
    LABELS = {
        WAITING: "Waiting",
        IN_PROGRESS: "In Progress",
        ON_HOLD: "On Hold",
        COMPLETED: "Completed",
        READY_FOR_PICKUP: "Ready for Pickup",
        CANCELLED: "Cancelled",
    }
    BADGE_CLASSES = {
        WAITING: "badge-waiting",
        IN_PROGRESS: "badge-in-progress",
        ON_HOLD: "badge-on-hold",
        COMPLETED: "badge-completed",
        READY_FOR_PICKUP: "badge-ready",
        CANCELLED: "badge-cancelled",
    }


class ServiceType:
    OIL_CHANGE = "oil_change"
    TIRE_ROTATION = "tire_rotation"
    BRAKE_SERVICE = "brake_service"
    ENGINE_REPAIR = "engine_repair"
    TRANSMISSION = "transmission"
    ELECTRICAL = "electrical"
    AC_HEATING = "ac_heating"
    SUSPENSION = "suspension"
    DIAGNOSTIC = "diagnostic"
    INSPECTION = "inspection"
    BODYWORK = "bodywork"
    OTHER = "other"

    ALL = [
        OIL_CHANGE, TIRE_ROTATION, BRAKE_SERVICE, ENGINE_REPAIR,
        TRANSMISSION, ELECTRICAL, AC_HEATING, SUSPENSION,
        DIAGNOSTIC, INSPECTION, BODYWORK, OTHER,
    ]
    LABELS = {
        OIL_CHANGE: "Oil Change",
        TIRE_ROTATION: "Tire Rotation / Replacement",
        BRAKE_SERVICE: "Brake Service",
        ENGINE_REPAIR: "Engine Repair",
        TRANSMISSION: "Transmission Service",
        ELECTRICAL: "Electrical / Battery",
        AC_HEATING: "A/C & Heating",
        SUSPENSION: "Suspension / Steering",
        DIAGNOSTIC: "Diagnostic",
        INSPECTION: "Inspection",
        BODYWORK: "Body Work",
        OTHER: "Other / General",
    }


class UrgencyLevel:
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

    ALL = [NORMAL, HIGH, CRITICAL]
    LABELS = {NORMAL: "Normal", HIGH: "High Priority", CRITICAL: "Critical / ASAP"}


class ServiceTicket(db.Model):
    __tablename__ = "service_tickets"

    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    shop_id = db.Column(
        db.Integer, db.ForeignKey("shops.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Foreign keys
    vehicle_id = db.Column(
        db.Integer, db.ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assigned_mechanic_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    created_by_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    # Service details
    service_type = db.Column(db.String(50), nullable=False, default=ServiceType.OTHER)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.String(30), nullable=False, default=TicketStatus.WAITING, index=True
    )
    urgency = db.Column(
        db.String(20), nullable=False, default=UrgencyLevel.NORMAL, index=True
    )

    # Mileage snapshot at intake
    mileage_in = db.Column(db.Integer)

    # Customer-reported complaint
    customer_complaint = db.Column(db.Text)

    # Estimated completion
    estimated_hours = db.Column(db.Numeric(4, 1))
    promised_time = db.Column(db.DateTime(timezone=True))

    # Completion tracking
    completed_at = db.Column(db.DateTime(timezone=True))
    picked_up_at = db.Column(db.DateTime(timezone=True))

    # Timestamps
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    notes = db.relationship(
        "ServiceNote",
        backref="ticket",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="ServiceNote.created_at.desc()",
    )
    status_history = db.relationship(
        "StatusHistory",
        backref="ticket",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="StatusHistory.changed_at.desc()",
    )

    @property
    def status_label(self):
        return TicketStatus.LABELS.get(self.status, self.status)

    @property
    def urgency_label(self):
        return UrgencyLevel.LABELS.get(self.urgency, self.urgency)

    @property
    def service_type_label(self):
        return ServiceType.LABELS.get(self.service_type, self.service_type)

    @property
    def status_badge_class(self):
        return TicketStatus.BADGE_CLASSES.get(self.status, "badge-default")

    @property
    def is_urgent(self):
        return self.urgency in (UrgencyLevel.HIGH, UrgencyLevel.CRITICAL)

    @property
    def is_active(self):
        return self.status in TicketStatus.ACTIVE

    @property
    def customer(self):
        return self.vehicle.owner if self.vehicle else None

    def __repr__(self):
        return f"<ServiceTicket #{self.ticket_number} [{self.status}]>"


class StatusHistory(db.Model):
    __tablename__ = "status_history"

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(
        db.Integer, db.ForeignKey("service_tickets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    changed_by_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL")
    )
    from_status = db.Column(db.String(30))
    to_status = db.Column(db.String(30), nullable=False)
    note = db.Column(db.String(200))
    changed_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
