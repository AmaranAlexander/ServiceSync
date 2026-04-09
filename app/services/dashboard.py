from datetime import datetime, timezone, date
from sqlalchemy import func
from app import db
from app.models.ticket import ServiceTicket, TicketStatus, UrgencyLevel
from app.models.user import User, Role


def get_dashboard_metrics(shop_id):
    today_start = datetime.combine(date.today(), datetime.min.time()).replace(tzinfo=timezone.utc)

    total_open = ServiceTicket.query.filter(
        ServiceTicket.shop_id == shop_id,
        ServiceTicket.status.in_(TicketStatus.ACTIVE),
    ).count()

    waiting = ServiceTicket.query.filter_by(shop_id=shop_id, status=TicketStatus.WAITING).count()
    in_progress = ServiceTicket.query.filter_by(shop_id=shop_id, status=TicketStatus.IN_PROGRESS).count()
    on_hold = ServiceTicket.query.filter_by(shop_id=shop_id, status=TicketStatus.ON_HOLD).count()
    ready_for_pickup = ServiceTicket.query.filter_by(shop_id=shop_id, status=TicketStatus.READY_FOR_PICKUP).count()

    urgent_tickets = ServiceTicket.query.filter(
        ServiceTicket.shop_id == shop_id,
        ServiceTicket.urgency.in_([UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]),
        ServiceTicket.status.in_(TicketStatus.ACTIVE),
    ).order_by(ServiceTicket.urgency.desc(), ServiceTicket.created_at.asc()).limit(10).all()

    completed_today = ServiceTicket.query.filter(
        ServiceTicket.shop_id == shop_id,
        ServiceTicket.completed_at >= today_start,
    ).count()

    mechanic_workload = (
        db.session.query(User, func.count(ServiceTicket.id).label("job_count"))
        .outerjoin(
            ServiceTicket,
            (ServiceTicket.assigned_mechanic_id == User.id)
            & (ServiceTicket.shop_id == shop_id)
            & (ServiceTicket.status.in_(TicketStatus.ACTIVE)),
        )
        .filter(User.role == Role.MECHANIC, User.is_active == True, User.shop_id == shop_id)
        .group_by(User.id)
        .order_by(func.count(ServiceTicket.id).desc())
        .all()
    )

    recent_tickets = (
        ServiceTicket.query
        .filter(
            ServiceTicket.shop_id == shop_id,
            ServiceTicket.status.in_(TicketStatus.ACTIVE + [TicketStatus.READY_FOR_PICKUP]),
        )
        .order_by(ServiceTicket.updated_at.desc())
        .limit(8)
        .all()
    )

    return {
        "total_open": total_open,
        "waiting": waiting,
        "in_progress": in_progress,
        "on_hold": on_hold,
        "ready_for_pickup": ready_for_pickup,
        "completed_today": completed_today,
        "urgent_tickets": urgent_tickets,
        "mechanic_workload": mechanic_workload,
        "recent_tickets": recent_tickets,
    }


def get_mechanic_metrics(mechanic_id, shop_id):
    today_start = datetime.combine(date.today(), datetime.min.time()).replace(tzinfo=timezone.utc)

    active_jobs = ServiceTicket.query.filter(
        ServiceTicket.shop_id == shop_id,
        ServiceTicket.assigned_mechanic_id == mechanic_id,
        ServiceTicket.status.in_(TicketStatus.ACTIVE),
    ).order_by(ServiceTicket.urgency.desc(), ServiceTicket.created_at.asc()).all()

    completed_today = ServiceTicket.query.filter(
        ServiceTicket.shop_id == shop_id,
        ServiceTicket.assigned_mechanic_id == mechanic_id,
        ServiceTicket.completed_at >= today_start,
    ).count()

    return {
        "active_jobs": active_jobs,
        "active_count": len(active_jobs),
        "completed_today": completed_today,
    }
