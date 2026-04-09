from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.shop import Shop
from app.models.user import User, Role
from app.forms.auth import LoginForm
from app.forms.register import RegisterForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip().lower()).first()
        if user and user.is_active and user.check_password(form.password.data):
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get("next")
            flash(f"Welcome back, {user.full_name}.", "success")
            return redirect(next_page or url_for("dashboard.index"))
        flash("Invalid username or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip().lower()
        email = form.email.data.strip().lower()

        if User.query.filter_by(username=username).first():
            flash("That username is already taken.", "danger")
            return render_template("auth/register.html", form=form)

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "danger")
            return render_template("auth/register.html", form=form)

        if form.action.data == "create":
            shop = Shop(
                name=form.shop_name.data.strip(),
                join_code=Shop.generate_join_code(),
            )
            db.session.add(shop)
            db.session.flush()

            user = User(
                username=username,
                email=email,
                full_name=form.full_name.data.strip(),
                role=Role.MANAGER,
                shop_id=shop.id,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash(
                f"Shop '{shop.name}' created. Your join code is {shop.join_code} — "
                "share it with your team so they can sign up.",
                "success",
            )

        else:  # join
            shop = Shop.query.filter_by(
                join_code=form.join_code.data.strip().upper()
            ).first()
            if not shop:
                flash("Join code not found. Double-check with your manager.", "danger")
                return render_template("auth/register.html", form=form)

            user = User(
                username=username,
                email=email,
                full_name=form.full_name.data.strip(),
                role=Role.FRONT_DESK,
                shop_id=shop.id,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash(f"Account created. Welcome to {shop.name}!", "success")

        login_user(user)
        return redirect(url_for("dashboard.index"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))
