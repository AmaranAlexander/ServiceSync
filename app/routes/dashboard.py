from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.services.dashboard import get_dashboard_metrics, get_mechanic_metrics

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    if current_user.is_mechanic:
        metrics = get_mechanic_metrics(current_user.id, current_user.shop_id)
        return render_template("dashboard/mechanic.html", metrics=metrics)

    metrics = get_dashboard_metrics(current_user.shop_id)
    return render_template("dashboard/index.html", metrics=metrics)
