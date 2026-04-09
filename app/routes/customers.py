from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models.customer import Customer
from app.models.vehicle import Vehicle
from app.forms.customer import CustomerForm, VehicleForm

customers_bp = Blueprint("customers", __name__, url_prefix="/customers")


@customers_bp.route("/")
@login_required
def list_customers():
    search = request.args.get("q", "").strip()
    query = Customer.query.filter_by(shop_id=current_user.shop_id)

    if search:
        query = query.filter(
            db.or_(
                Customer.first_name.ilike(f"%{search}%"),
                Customer.last_name.ilike(f"%{search}%"),
                Customer.phone.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%"),
            )
        )

    customers = query.order_by(Customer.last_name, Customer.first_name).all()
    return render_template("customers/list.html", customers=customers, search=search)


@customers_bp.route("/new", methods=["GET", "POST"])
@login_required
def create_customer():
    if current_user.is_mechanic:
        abort(403)

    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(
            shop_id=current_user.shop_id,
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            phone=form.phone.data.strip(),
            email=form.email.data.strip() or None,
            address=form.address.data.strip() or None,
            notes=form.notes.data or None,
        )
        db.session.add(customer)
        db.session.commit()
        flash(f"Customer {customer.full_name} created.", "success")
        return redirect(url_for("customers.customer_detail", customer_id=customer.id))

    return render_template("customers/form.html", form=form, customer=None)


@customers_bp.route("/<int:customer_id>")
@login_required
def customer_detail(customer_id):
    customer = Customer.query.filter_by(
        id=customer_id, shop_id=current_user.shop_id
    ).first_or_404()
    vehicles = customer.vehicles.order_by(Vehicle.year.desc()).all()
    return render_template("customers/detail.html", customer=customer, vehicles=vehicles)


@customers_bp.route("/<int:customer_id>/edit", methods=["GET", "POST"])
@login_required
def edit_customer(customer_id):
    if current_user.is_mechanic:
        abort(403)

    customer = Customer.query.filter_by(
        id=customer_id, shop_id=current_user.shop_id
    ).first_or_404()
    form = CustomerForm(obj=customer)

    if form.validate_on_submit():
        customer.first_name = form.first_name.data.strip()
        customer.last_name = form.last_name.data.strip()
        customer.phone = form.phone.data.strip()
        customer.email = form.email.data.strip() or None
        customer.address = form.address.data.strip() or None
        customer.notes = form.notes.data or None
        db.session.commit()
        flash("Customer updated.", "success")
        return redirect(url_for("customers.customer_detail", customer_id=customer.id))

    return render_template("customers/form.html", form=form, customer=customer)


@customers_bp.route("/<int:customer_id>/vehicles/add", methods=["GET", "POST"])
@login_required
def add_vehicle(customer_id):
    if current_user.is_mechanic:
        abort(403)

    customer = Customer.query.filter_by(
        id=customer_id, shop_id=current_user.shop_id
    ).first_or_404()
    form = VehicleForm()

    if form.validate_on_submit():
        vehicle = Vehicle(
            customer_id=customer.id,
            make=form.make.data.strip(),
            model=form.model.data.strip(),
            year=form.year.data,
            color=form.color.data.strip() or None,
            license_plate=form.license_plate.data.strip().upper() or None,
            vin=form.vin.data.strip().upper() or None,
            mileage_in=form.mileage_in.data or None,
            engine=form.engine.data.strip() or None,
            transmission=form.transmission.data or None,
        )
        db.session.add(vehicle)
        db.session.commit()
        flash(f"Vehicle {vehicle.display_name} added.", "success")
        return redirect(url_for("customers.customer_detail", customer_id=customer.id))

    return render_template("customers/vehicle_form.html", form=form, customer=customer, vehicle=None)


@customers_bp.route("/<int:customer_id>/vehicles/<int:vehicle_id>/edit", methods=["GET", "POST"])
@login_required
def edit_vehicle(customer_id, vehicle_id):
    if current_user.is_mechanic:
        abort(403)

    customer = Customer.query.filter_by(
        id=customer_id, shop_id=current_user.shop_id
    ).first_or_404()
    vehicle = Vehicle.query.filter_by(id=vehicle_id, customer_id=customer_id).first_or_404()
    form = VehicleForm(obj=vehicle)

    if form.validate_on_submit():
        vehicle.make = form.make.data.strip()
        vehicle.model = form.model.data.strip()
        vehicle.year = form.year.data
        vehicle.color = form.color.data.strip() or None
        vehicle.license_plate = form.license_plate.data.strip().upper() or None
        vehicle.vin = form.vin.data.strip().upper() or None
        vehicle.mileage_in = form.mileage_in.data or None
        vehicle.engine = form.engine.data.strip() or None
        vehicle.transmission = form.transmission.data or None
        db.session.commit()
        flash("Vehicle updated.", "success")
        return redirect(url_for("customers.customer_detail", customer_id=customer.id))

    return render_template("customers/vehicle_form.html", form=form, customer=customer, vehicle=vehicle)
