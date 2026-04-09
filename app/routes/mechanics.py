from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.models.user import User, Role
from app.services.dashboard import get_mechanic_metrics

mechanics_bp = Blueprint("mechanics", __name__, url_prefix="/mechanics")


@mechanics_bp.route("/")
@login_required
def workload():
    if not (current_user.is_manager or current_user.is_front_desk):
        abort(403)

    mechanics = User.query.filter_by(
        role=Role.MECHANIC, is_active=True, shop_id=current_user.shop_id
    ).order_by(User.full_name).all()

    workloads = []
    for mechanic in mechanics:
        metrics = get_mechanic_metrics(mechanic.id, current_user.shop_id)
        workloads.append({"mechanic": mechanic, "metrics": metrics})

    return render_template("mechanics/workload.html", workloads=workloads)


@mechanics_bp.route("/<int:mechanic_id>")
@login_required
def mechanic_detail(mechanic_id):
    if current_user.is_mechanic and current_user.id != mechanic_id:
        abort(403)

    mechanic = User.query.filter_by(
        id=mechanic_id, role=Role.MECHANIC, shop_id=current_user.shop_id
    ).first_or_404()

    metrics = get_mechanic_metrics(mechanic_id, current_user.shop_id)
    return render_template("mechanics/detail.html", mechanic=mechanic, metrics=metrics)
