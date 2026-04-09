import secrets
import string
from datetime import datetime, timezone
from app import db


def _random_code(length=8):
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class Shop(db.Model):
    __tablename__ = "shops"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    join_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    members = db.relationship(
        "User", foreign_keys="User.shop_id", backref="shop", lazy="dynamic"
    )
    customers = db.relationship("Customer", backref="shop", lazy="dynamic")
    tickets = db.relationship("ServiceTicket", backref="shop", lazy="dynamic")

    @staticmethod
    def generate_join_code():
        """Generate a unique 8-character alphanumeric join code."""
        while True:
            code = _random_code(8)
            if not Shop.query.filter_by(join_code=code).first():
                return code

    def __repr__(self):
        return f"<Shop {self.name} [{self.join_code}]>"
