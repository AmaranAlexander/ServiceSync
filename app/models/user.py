from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Role:
    FRONT_DESK = "front_desk"
    MECHANIC = "mechanic"
    MANAGER = "manager"

    ALL = [FRONT_DESK, MECHANIC, MANAGER]
    LABELS = {
        FRONT_DESK: "Front Desk / Advisor",
        MECHANIC: "Mechanic / Technician",
        MANAGER: "Manager",
    }


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(32), nullable=False, default=Role.FRONT_DESK)
    phone = db.Column(db.String(20))
    shop_id = db.Column(
        db.Integer, db.ForeignKey("shops.id", ondelete="SET NULL"), index=True
    )
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_login = db.Column(db.DateTime(timezone=True))

    # Relationships
    assigned_tickets = db.relationship(
        "ServiceTicket",
        foreign_keys="ServiceTicket.assigned_mechanic_id",
        backref="mechanic",
        lazy="dynamic",
    )
    created_tickets = db.relationship(
        "ServiceTicket",
        foreign_keys="ServiceTicket.created_by_id",
        backref="creator",
        lazy="dynamic",
    )
    notes = db.relationship("ServiceNote", backref="author", lazy="dynamic")
    status_changes = db.relationship("StatusHistory", backref="changed_by", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def role_label(self):
        return Role.LABELS.get(self.role, self.role)

    @property
    def is_mechanic(self):
        return self.role == Role.MECHANIC

    @property
    def is_manager(self):
        return self.role == Role.MANAGER

    @property
    def is_front_desk(self):
        return self.role == Role.FRONT_DESK

    def __repr__(self):
        return f"<User {self.username} [{self.role}]>"
