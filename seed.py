"""
seed.py -- Populate the database with realistic demo data.
Run after schema changes:  python seed.py
"""
from datetime import datetime, timezone, timedelta
from app import create_app, db
from app.models.shop import Shop
from app.models.user import User, Role
from app.models.customer import Customer
from app.models.vehicle import Vehicle
from app.models.ticket import ServiceTicket, StatusHistory, TicketStatus, ServiceType, UrgencyLevel
from app.models.note import ServiceNote

app = create_app("development")

with app.app_context():
    db.drop_all()
    db.create_all()

    # -- Shop ----------------------------------------------------------------
    shop = Shop(name="Riverside Auto Service", join_code="DEMO1234")
    db.session.add(shop)
    db.session.flush()

    # -- Users ---------------------------------------------------------------
    manager = User(username="admin", email="admin@servicesync.com",
                   full_name="Sarah Kowalski", role=Role.MANAGER, shop_id=shop.id)
    manager.set_password("admin123")

    advisor = User(username="jmorris", email="jmorris@servicesync.com",
                   full_name="James Morris", role=Role.FRONT_DESK, shop_id=shop.id)
    advisor.set_password("password")

    mech1 = User(username="tdiaz", email="tdiaz@servicesync.com",
                 full_name="Tony Diaz", role=Role.MECHANIC, phone="555-0101", shop_id=shop.id)
    mech1.set_password("password")

    mech2 = User(username="lchen", email="lchen@servicesync.com",
                 full_name="Linda Chen", role=Role.MECHANIC, phone="555-0202", shop_id=shop.id)
    mech2.set_password("password")

    mech3 = User(username="rbrown", email="rbrown@servicesync.com",
                 full_name="Ray Brown", role=Role.MECHANIC, phone="555-0303", shop_id=shop.id)
    mech3.set_password("password")

    db.session.add_all([manager, advisor, mech1, mech2, mech3])
    db.session.flush()

    # -- Customers + Vehicles ------------------------------------------------
    def make_customer(first, last, phone, email=None, address=None, notes=None):
        c = Customer(shop_id=shop.id, first_name=first, last_name=last,
                     phone=phone, email=email, address=address, notes=notes)
        db.session.add(c)
        db.session.flush()
        return c

    def make_vehicle(customer, make, model, year, plate, vin=None, mileage=None,
                     color=None, engine=None, trans=None):
        v = Vehicle(customer_id=customer.id, make=make, model=model, year=year,
                    license_plate=plate, vin=vin, mileage_in=mileage,
                    color=color, engine=engine, transmission=trans)
        db.session.add(v)
        db.session.flush()
        return v

    c1 = make_customer("Marcus", "Riley", "555-210-3344", "m.riley@email.com", "412 Elm St")
    v1 = make_vehicle(c1, "Honda", "Accord", 2018, "ABC-1234", mileage=87400,
                      color="Blue", engine="2.0L Turbo", trans="automatic")
    v1b = make_vehicle(c1, "Ford", "F-150", 2021, "TRK-4490", mileage=34200,
                       color="Black", engine="5.0L V8", trans="automatic")

    c2 = make_customer("Diana", "Okafor", "555-774-9921", "dokafor@gmail.com",
                       notes="VIP -- always call before closing")
    v2 = make_vehicle(c2, "BMW", "330i", 2020, "BMW-7731", mileage=51000,
                      color="White", engine="2.0L I4 Turbo", trans="automatic")

    c3 = make_customer("Pete", "Hernandez", "555-443-6677")
    v3 = make_vehicle(c3, "Toyota", "Camry", 2016, "CAM-0088", mileage=114300,
                      color="Silver", engine="2.5L 4-cyl", trans="automatic")

    c4 = make_customer("Janet", "Wu", "555-882-5500", "jwu@work.com")
    v4 = make_vehicle(c4, "Chevrolet", "Malibu", 2019, "MLB-3391", mileage=62000,
                      color="Red", engine="1.5L Turbo", trans="automatic")

    c5 = make_customer("Omar", "Hassan", "555-331-7845")
    v5 = make_vehicle(c5, "Dodge", "Charger", 2015, "CHG-5500", mileage=143000,
                      color="Gray", engine="3.6L V6", trans="automatic")

    # -- Tickets -------------------------------------------------------------
    now = datetime.now(timezone.utc)

    def make_ticket(number, vehicle, stype, desc, status, urgency, mechanic=None,
                    complaint=None, mileage=None, est_hours=None, promised=None,
                    created_offset_hrs=0, completed=False):
        t = ServiceTicket(
            ticket_number=number,
            shop_id=shop.id,
            vehicle_id=vehicle.id,
            service_type=stype,
            description=desc,
            customer_complaint=complaint,
            status=status,
            urgency=urgency,
            assigned_mechanic_id=mechanic.id if mechanic else None,
            created_by_id=advisor.id,
            mileage_in=mileage,
            estimated_hours=est_hours,
            promised_time=promised,
            created_at=now - timedelta(hours=created_offset_hrs),
        )
        if completed or status in [TicketStatus.COMPLETED, TicketStatus.READY_FOR_PICKUP]:
            t.completed_at = now - timedelta(hours=max(0, created_offset_hrs - 2))
        db.session.add(t)
        db.session.flush()
        return t

    t1 = make_ticket("260409-001", v1, ServiceType.BRAKE_SERVICE,
                     "Replace front brake pads and rotors. Left front making grinding noise.",
                     TicketStatus.IN_PROGRESS, UrgencyLevel.HIGH, mechanic=mech1,
                     complaint="Grinding noise when braking, especially at low speeds",
                     mileage=87400, est_hours=2.5,
                     promised=now + timedelta(hours=3), created_offset_hrs=4)

    t2 = make_ticket("260409-002", v2, ServiceType.DIAGNOSTIC,
                     "Check engine light on. Customer reports rough idle and occasional stall.",
                     TicketStatus.IN_PROGRESS, UrgencyLevel.CRITICAL, mechanic=mech2,
                     complaint="Car stalls at red lights, rough idle, CEL on for 2 days",
                     mileage=51000, est_hours=1.5, created_offset_hrs=2)

    t3 = make_ticket("260409-003", v3, ServiceType.OIL_CHANGE,
                     "Full synthetic oil change, 5W-30. Tire rotation included.",
                     TicketStatus.WAITING, UrgencyLevel.NORMAL,
                     mileage=114300, est_hours=0.75,
                     promised=now + timedelta(hours=2), created_offset_hrs=1)

    t4 = make_ticket("260409-004", v4, ServiceType.AC_HEATING,
                     "A/C blowing warm air. Recharge refrigerant and inspect for leaks.",
                     TicketStatus.WAITING, UrgencyLevel.HIGH,
                     complaint="No cold air, A/C makes clicking sound when turned on",
                     mileage=62000, est_hours=2.0, created_offset_hrs=0.5)

    t5 = make_ticket("260409-005", v5, ServiceType.ENGINE_REPAIR,
                     "Coolant leak traced to cracked upper hose. Replace hose and flush cooling system.",
                     TicketStatus.ON_HOLD, UrgencyLevel.HIGH, mechanic=mech3,
                     complaint="Temp gauge rising, sweet smell from engine bay",
                     mileage=143000, est_hours=3.0, created_offset_hrs=5)

    t6 = make_ticket("260409-006", v1b, ServiceType.TIRE_ROTATION,
                     "Rotate all 4 tires. Check tread depth and air pressure.",
                     TicketStatus.READY_FOR_PICKUP, UrgencyLevel.NORMAL, mechanic=mech1,
                     mileage=34200, est_hours=0.5, created_offset_hrs=6, completed=True)

    t7 = make_ticket("260408-012", v3, ServiceType.INSPECTION,
                     "Annual state safety inspection.",
                     TicketStatus.COMPLETED, UrgencyLevel.NORMAL, mechanic=mech2,
                     mileage=114000, est_hours=1.0, created_offset_hrs=26, completed=True)

    # -- Notes ---------------------------------------------------------------
    db.session.add_all([
        ServiceNote(ticket_id=t1.id, author_id=mech1.id,
                    body="Left front caliper also looks worn, flagging for advisor approval to replace."),
        ServiceNote(ticket_id=t1.id, author_id=advisor.id,
                    body="Customer approved caliper replacement. Parts ordered, should be here by 2pm."),
        ServiceNote(ticket_id=t2.id, author_id=mech2.id,
                    body="Pulled codes: P0301 (cylinder 1 misfire), P0171 (lean condition). Checking injectors now."),
        ServiceNote(ticket_id=t5.id, author_id=mech3.id,
                    body="Put on hold -- waiting on upper radiator hose from supplier. ETA 3 hours."),
        ServiceNote(ticket_id=t5.id, author_id=advisor.id,
                    body="Called customer, informed of delay. They're okay waiting until tomorrow if needed."),
        ServiceNote(ticket_id=t6.id, author_id=mech1.id,
                    body="Completed. Front right tire at 3/32 tread -- recommend replacement soon."),
    ])

    # -- Status History ------------------------------------------------------
    db.session.add_all([
        StatusHistory(ticket_id=t1.id, changed_by_id=advisor.id,
                      from_status=None, to_status=TicketStatus.WAITING, note="Ticket created"),
        StatusHistory(ticket_id=t1.id, changed_by_id=mech1.id,
                      from_status=TicketStatus.WAITING, to_status=TicketStatus.IN_PROGRESS,
                      note="Starting brake inspection"),
        StatusHistory(ticket_id=t2.id, changed_by_id=advisor.id,
                      from_status=None, to_status=TicketStatus.WAITING, note="Ticket created"),
        StatusHistory(ticket_id=t2.id, changed_by_id=mech2.id,
                      from_status=TicketStatus.WAITING, to_status=TicketStatus.IN_PROGRESS),
        StatusHistory(ticket_id=t5.id, changed_by_id=advisor.id,
                      from_status=None, to_status=TicketStatus.WAITING, note="Ticket created"),
        StatusHistory(ticket_id=t5.id, changed_by_id=mech3.id,
                      from_status=TicketStatus.WAITING, to_status=TicketStatus.IN_PROGRESS),
        StatusHistory(ticket_id=t5.id, changed_by_id=mech3.id,
                      from_status=TicketStatus.IN_PROGRESS, to_status=TicketStatus.ON_HOLD,
                      note="Waiting on parts"),
        StatusHistory(ticket_id=t6.id, changed_by_id=advisor.id,
                      from_status=None, to_status=TicketStatus.WAITING, note="Ticket created"),
        StatusHistory(ticket_id=t6.id, changed_by_id=mech1.id,
                      from_status=TicketStatus.WAITING, to_status=TicketStatus.IN_PROGRESS),
        StatusHistory(ticket_id=t6.id, changed_by_id=mech1.id,
                      from_status=TicketStatus.IN_PROGRESS, to_status=TicketStatus.READY_FOR_PICKUP,
                      note="Job complete"),
    ])

    db.session.commit()
    print("Database seeded successfully.")
    print()
    print("  Shop: Riverside Auto Service")
    print("  Join Code: DEMO1234")
    print()
    print("  Login credentials:")
    print("  -----------------------------------------")
    print("  Manager    : admin     / admin123")
    print("  Front Desk : jmorris   / password")
    print("  Mechanic   : tdiaz     / password")
    print("  Mechanic   : lchen     / password")
    print("  Mechanic   : rbrown    / password")
