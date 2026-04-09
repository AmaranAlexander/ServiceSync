from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, IntegerField,
    DecimalField, DateTimeLocalField, SubmitField,
)
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from app.models.ticket import TicketStatus, ServiceType, UrgencyLevel


def mechanic_choices():
    from flask_login import current_user
    from app.models.user import User, Role
    mechanics = User.query.filter_by(
        role=Role.MECHANIC, is_active=True, shop_id=current_user.shop_id
    ).order_by(User.full_name).all()
    choices = [("", "— Unassigned —")]
    choices += [(str(m.id), m.full_name) for m in mechanics]
    return choices


class ServiceTicketForm(FlaskForm):
    vehicle_id = SelectField("Vehicle", coerce=int, validators=[DataRequired()])
    service_type = SelectField(
        "Service Type",
        choices=[(k, v) for k, v in ServiceType.LABELS.items()],
        validators=[DataRequired()],
    )
    description = TextAreaField(
        "Work Description",
        validators=[DataRequired(), Length(1, 2000)],
        render_kw={"rows": 4, "placeholder": "Describe the service or repairs needed..."},
    )
    customer_complaint = TextAreaField(
        "Customer Complaint",
        validators=[Optional(), Length(0, 1000)],
        render_kw={"rows": 3, "placeholder": "What did the customer report?"},
    )
    urgency = SelectField(
        "Urgency",
        choices=[(k, v) for k, v in UrgencyLevel.LABELS.items()],
        default=UrgencyLevel.NORMAL,
    )
    mileage_in = IntegerField(
        "Mileage In",
        validators=[Optional(), NumberRange(min=0, max=999999)],
        render_kw={"placeholder": "e.g. 84500"},
    )
    assigned_mechanic_id = SelectField("Assign Mechanic", validators=[Optional()])
    estimated_hours = DecimalField(
        "Estimated Hours",
        validators=[Optional(), NumberRange(min=0.1, max=99)],
        places=1,
        render_kw={"placeholder": "e.g. 2.5"},
    )
    promised_time = DateTimeLocalField(
        "Promised By",
        format="%Y-%m-%dT%H:%M",
        validators=[Optional()],
    )
    submit = SubmitField("Save Ticket")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assigned_mechanic_id.choices = mechanic_choices()


class UpdateStatusForm(FlaskForm):
    status = SelectField(
        "New Status",
        choices=[(k, v) for k, v in TicketStatus.LABELS.items()],
        validators=[DataRequired()],
    )
    note = StringField(
        "Status Note (optional)",
        validators=[Optional(), Length(0, 200)],
        render_kw={"placeholder": "e.g. Waiting on parts..."},
    )
    submit = SubmitField("Update Status")


class ServiceNoteForm(FlaskForm):
    body = TextAreaField(
        "Note",
        validators=[DataRequired(), Length(1, 2000)],
        render_kw={"rows": 3, "placeholder": "Add an internal update or observation..."},
    )
    submit = SubmitField("Add Note")
