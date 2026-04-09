from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Optional, Email, Length, NumberRange


class CustomerForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(1, 64)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(1, 64)])
    phone = StringField(
        "Phone",
        validators=[DataRequired(), Length(7, 20)],
        render_kw={"placeholder": "e.g. 555-867-5309"},
    )
    email = StringField("Email", validators=[Optional(), Email(), Length(0, 120)])
    address = StringField("Address", validators=[Optional(), Length(0, 200)])
    notes = TextAreaField(
        "Customer Notes",
        validators=[Optional(), Length(0, 1000)],
        render_kw={"rows": 3, "placeholder": "VIP, preferred contact method, etc."},
    )
    submit = SubmitField("Save Customer")


class VehicleForm(FlaskForm):
    make = StringField("Make", validators=[DataRequired(), Length(1, 64)], render_kw={"placeholder": "e.g. Toyota"})
    model = StringField("Model", validators=[DataRequired(), Length(1, 64)], render_kw={"placeholder": "e.g. Camry"})
    year = IntegerField(
        "Year",
        validators=[DataRequired(), NumberRange(min=1900, max=2100)],
        render_kw={"placeholder": "e.g. 2019"},
    )
    color = StringField("Color", validators=[Optional(), Length(0, 32)], render_kw={"placeholder": "e.g. Silver"})
    license_plate = StringField("License Plate", validators=[Optional(), Length(0, 20)])
    vin = StringField("VIN", validators=[Optional(), Length(0, 17)], render_kw={"placeholder": "17-character VIN"})
    mileage_in = IntegerField(
        "Current Mileage",
        validators=[Optional(), NumberRange(min=0, max=999999)],
        render_kw={"placeholder": "e.g. 52300"},
    )
    engine = StringField("Engine", validators=[Optional(), Length(0, 50)], render_kw={"placeholder": "e.g. 2.5L 4-cyl"})
    transmission = SelectField(
        "Transmission",
        choices=[("", "Unknown"), ("automatic", "Automatic"), ("manual", "Manual"), ("cvt", "CVT")],
        validators=[Optional()],
    )
    submit = SubmitField("Save Vehicle")
