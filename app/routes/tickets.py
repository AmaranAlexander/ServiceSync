from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models.ticket import ServiceTicket, StatusHistory, TicketStatus, UrgencyLevel
from app.models.note import ServiceNote
from app.models.vehicle import Vehicle
from app.models.customer import Customer
from app.models.user import User, Role
from app.forms.ticket import ServiceTicketForm, UpdateStatusForm, ServiceNoteForm

tickets_bp = Blueprint("tickets", __name__, url_prefix="/tickets")


def _generate_ticket_number():
    from datetime import date
    prefix = date.today().strftime("%y%m%d")
    last = (
        ServiceTicket.query
        .filter(
            ServiceTicket.shop_id == current_user.shop_id,
            ServiceTicket.ticket_number.like(f"{prefix}%"),
        )
        .order_by(ServiceTicket.ticket_number.desc())
        .first()
    )
    seq = 1
    if last:
        try:
            seq = int(last.ticket_number[-3:]) + 1
        except (ValueError, IndexError):
            seq = 1
    return f"{prefix}-{seq:03d}"


def _vehicle_choices():
    vehicles = (
        Vehicle.query
        .join(Vehicle.owner)
        .filter(Customer.shop_id == current_user.shop_id)
        .order_by(Vehicle.make, Vehicle.model)
        .all()
    )
    return [(v.id, f"{v.owner.full_name} — {v.display_name} ({v.license_plate or 'no plate'})") for v in vehicles]


@tickets_bp.route("/")
@login_required
def list_tickets():
    query = ServiceTicket.query.filter_by(shop_id=current_user.shop_id)

    if current_user.is_mechanic:
        query = query.filter_by(assigned_mechanic_id=current_user.id)

    status_filter = request.args.get("status", "")
    urgency_filter = request.args.get("urgency", "")
    mechanic_filter = request.args.get("mechanic", "")
    search = request.args.get("q", "").strip()

    if status_filter:
        query = query.filter_by(status=status_filter)
    if urgency_filter:
        query = query.filter_by(urgency=urgency_filter)
    if mechanic_filter and current_user.is_manager:
        query = query.filter_by(assigned_mechanic_id=int(mechanic_filter))
    if search:
        query = (
            query
            .join(ServiceTicket.vehicle)
            .join(Vehicle.owner)
            .filter(
                db.or_(
                    ServiceTicket.ticket_number.ilike(f"%{search}%"),
                    Vehicle.license_plate.ilike(f"%{search}%"),
                    Customer.first_name.ilike(f"%{search}%"),
                    Customer.last_name.ilike(f"%{search}%"),
                    Customer.phone.ilike(f"%{search}%"),
                )
            )
        )

    tickets = (
        query
        .order_by(
            db.case(
                (ServiceTicket.urgency == UrgencyLevel.CRITICAL, 0),
                (ServiceTicket.urgency == UrgencyLevel.HIGH, 1),
                else_=2,
            ),
            ServiceTicket.created_at.asc(),
        )
        .all()
    )

    mechanics = User.query.filter_by(
        role=Role.MECHANIC, is_active=True, shop_id=current_user.shop_id
    ).order_by(User.full_name).all()

    return render_template(
        "tickets/list.html",
        tickets=tickets,
        mechanics=mechanics,
        statuses=TicketStatus.LABELS,
        urgencies=UrgencyLevel.LABELS,
        filters={"status": status_filter, "urgency": urgency_filter, "mechanic": mechanic_filter, "q": search},
    )


@tickets_bp.route("/new", methods=["GET", "POST"])
@login_required
def create_ticket():
    if current_user.is_mechanic:
        abort(403)

    form = ServiceTicketForm()
    form.vehicle_id.choices = _vehicle_choices()

    if request.method == "GET" and request.args.get("vehicle_id"):
        form.vehicle_id.data = int(request.args.get("vehicle_id"))

    if form.validate_on_submit():
        ticket = ServiceTicket(
            ticket_number=_generate_ticket_number(),
            shop_id=current_user.shop_id,
            vehicle_id=form.vehicle_id.data,
            service_type=form.service_type.data,
            description=form.description.data,
            customer_complaint=form.customer_complaint.data or None,
            urgency=form.urgency.data,
            mileage_in=form.mileage_in.data or None,
            estimated_hours=form.estimated_hours.data or None,
            promised_time=form.promised_time.data or None,
            status=TicketStatus.WAITING,
            created_by_id=current_user.id,
        )
        mechanic_id = form.assigned_mechanic_id.data
        if mechanic_id:
            ticket.assigned_mechanic_id = int(mechanic_id)

        db.session.add(ticket)
        db.session.flush()

        history = StatusHistory(
            ticket_id=ticket.id,
            changed_by_id=current_user.id,
            from_status=None,
            to_status=TicketStatus.WAITING,
            note="Ticket created",
        )
        db.session.add(history)
        db.session.commit()

        flash(f"Ticket #{ticket.ticket_number} created.", "success")
        return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))

    return render_template("tickets/form.html", form=form, ticket=None)


@tickets_bp.route("/<int:ticket_id>")
@login_required
def ticket_detail(ticket_id):
    ticket = ServiceTicket.query.filter_by(
        id=ticket_id, shop_id=current_user.shop_id
    ).first_or_404()

    if current_user.is_mechanic and ticket.assigned_mechanic_id != current_user.id:
        abort(403)

    status_form = UpdateStatusForm(prefix="status")
    status_form.status.data = ticket.status
    note_form = ServiceNoteForm(prefix="note")

    return render_template(
        "tickets/detail.html",
        ticket=ticket,
        status_form=status_form,
        note_form=note_form,
    )


@tickets_bp.route("/<int:ticket_id>/edit", methods=["GET", "POST"])
@login_required
def edit_ticket(ticket_id):
    ticket = ServiceTicket.query.filter_by(
        id=ticket_id, shop_id=current_user.shop_id
    ).first_or_404()

    if current_user.is_mechanic:
        abort(403)

    form = ServiceTicketForm(obj=ticket)
    form.vehicle_id.choices = _vehicle_choices()

    if form.validate_on_submit():
        ticket.vehicle_id = form.vehicle_id.data
        ticket.service_type = form.service_type.data
        ticket.description = form.description.data
        ticket.customer_complaint = form.customer_complaint.data or None
        ticket.urgency = form.urgency.data
        ticket.mileage_in = form.mileage_in.data or None
        ticket.estimated_hours = form.estimated_hours.data or None
        ticket.promised_time = form.promised_time.data or None
        mechanic_id = form.assigned_mechanic_id.data
        ticket.assigned_mechanic_id = int(mechanic_id) if mechanic_id else None
        ticket.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        flash("Ticket updated.", "success")
        return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))

    return render_template("tickets/form.html", form=form, ticket=ticket)


@tickets_bp.route("/<int:ticket_id>/update-status", methods=["POST"])
@login_required
def update_status(ticket_id):
    ticket = ServiceTicket.query.filter_by(
        id=ticket_id, shop_id=current_user.shop_id
    ).first_or_404()

    if current_user.is_mechanic and ticket.assigned_mechanic_id != current_user.id:
        abort(403)

    form = UpdateStatusForm(prefix="status")
    if form.validate_on_submit():
        old_status = ticket.status
        new_status = form.status.data

        if old_status != new_status:
            ticket.status = new_status
            ticket.updated_at = datetime.now(timezone.utc)

            if new_status == TicketStatus.COMPLETED:
                ticket.completed_at = datetime.now(timezone.utc)
            if new_status == TicketStatus.READY_FOR_PICKUP and not ticket.completed_at:
                ticket.completed_at = datetime.now(timezone.utc)

            history = StatusHistory(
                ticket_id=ticket.id,
                changed_by_id=current_user.id,
                from_status=old_status,
                to_status=new_status,
                note=form.note.data or None,
            )
            db.session.add(history)
            db.session.commit()
            flash(f"Status updated to {TicketStatus.LABELS[new_status]}.", "success")
        else:
            flash("Status unchanged.", "info")

    return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))


@tickets_bp.route("/<int:ticket_id>/add-note", methods=["POST"])
@login_required
def add_note(ticket_id):
    ticket = ServiceTicket.query.filter_by(
        id=ticket_id, shop_id=current_user.shop_id
    ).first_or_404()

    if current_user.is_mechanic and ticket.assigned_mechanic_id != current_user.id:
        abort(403)

    form = ServiceNoteForm(prefix="note")
    if form.validate_on_submit():
        note = ServiceNote(
            ticket_id=ticket.id,
            author_id=current_user.id,
            body=form.body.data,
        )
        db.session.add(note)
        ticket.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        flash("Note added.", "success")

    return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))


@tickets_bp.route("/<int:ticket_id>/delete", methods=["POST"])
@login_required
def delete_ticket(ticket_id):
    if not current_user.is_manager:
        abort(403)

    ticket = ServiceTicket.query.filter_by(
        id=ticket_id, shop_id=current_user.shop_id
    ).first_or_404()

    db.session.delete(ticket)
    db.session.commit()
    flash(f"Ticket #{ticket.ticket_number} deleted.", "warning")
    return redirect(url_for("tickets.list_tickets"))
