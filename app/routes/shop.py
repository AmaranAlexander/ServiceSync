from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models.user import User, Role

shop_bp = Blueprint("shop", __name__, url_prefix="/shop")


@shop_bp.route("/settings")
@login_required
def settings():
    members = (
        User.query
        .filter_by(shop_id=current_user.shop_id, is_active=True)
        .order_by(User.role, User.full_name)
        .all()
    )
    return render_template("shop/settings.html", shop=current_user.shop, members=members)


@shop_bp.route("/members/<int:user_id>/role", methods=["POST"])
@login_required
def update_member_role(user_id):
    if not current_user.is_manager:
        abort(403)

    member = User.query.filter_by(id=user_id, shop_id=current_user.shop_id).first_or_404()

    if member.id == current_user.id:
        flash("You cannot change your own role.", "warning")
        return redirect(url_for("shop.settings"))

    new_role = request.form.get("role")
    if new_role not in Role.ALL:
        flash("Invalid role.", "danger")
        return redirect(url_for("shop.settings"))

    member.role = new_role
    db.session.commit()
    flash(f"{member.full_name}'s role updated to {member.role_label}.", "success")
    return redirect(url_for("shop.settings"))
