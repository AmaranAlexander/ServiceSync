from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class RegisterForm(FlaskForm):
    full_name = StringField(
        "Full Name",
        validators=[DataRequired(), Length(1, 120)],
        render_kw={"placeholder": "e.g. Jane Smith"},
    )
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(3, 64)],
        render_kw={"placeholder": "e.g. janesmith"},
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(1, 120)],
        render_kw={"placeholder": "you@example.com"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(8, 128)],
        render_kw={"placeholder": "At least 8 characters"},
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    action = RadioField(
        "Account Setup",
        choices=[("create", "Create a new shop"), ("join", "Join an existing shop")],
        default="create",
    )
    shop_name = StringField(
        "Shop Name",
        validators=[Optional(), Length(1, 120)],
        render_kw={"placeholder": "e.g. Mike's Auto Service"},
    )
    join_code = StringField(
        "Join Code",
        validators=[Optional(), Length(6, 12)],
        render_kw={"placeholder": "e.g. SHOP1234 — ask your manager"},
    )
    submit = SubmitField("Create Account")

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        if self.action.data == "create" and not (self.shop_name.data or "").strip():
            self.shop_name.errors.append("Shop name is required.")
            return False
        if self.action.data == "join" and not (self.join_code.data or "").strip():
            self.join_code.errors.append("Join code is required.")
            return False
        return True
