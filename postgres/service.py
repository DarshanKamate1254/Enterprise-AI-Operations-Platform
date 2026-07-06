import os
import csv
import sys
from datetime import date
from typing import Dict, Any
from sqlalchemy.orm import Session

# Ensure imports resolve
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import engine, Base
import models
import schemas
import repositories


def init_db():
    """
    Initializes the database schema by creating all tables.
    """
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialization complete.")


def parse_date(date_str: str) -> date:
    """Helper to parse ISO date string (YYYY-MM-DD) or return None."""
    if not date_str or date_str.lower() == "null":
        return None
    return date.fromisoformat(date_str)


def parse_nullable_int(int_str: str) -> Any:
    """Helper to parse int or return None if empty."""
    if not int_str or int_str.lower() == "null" or int_str == "":
        return None
    return int(int_str)


def seed_db_from_csv(session: Session, data_dir: str):
    """
    Populates database tables from the fictional CSV files in data_dir,
    sequentially following relational dependencies:
    Departments -> Employees -> Users -> Customers -> Products -> Inventory -> Orders -> Tickets.
    """
    print("====================================================")
    print(f"Starting Database Seeding from: {data_dir}")
    print("====================================================")

    # 1. Seed Departments
    dept_file = os.path.join(data_dir, "departments.csv")
    if os.path.exists(dept_file):
        print("Seeding departments...")
        with open(dept_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Validate input data
                schema = schemas.DepartmentCreate(
                    name=row["name"],
                    description=row["description"],
                    cost_center=row["cost_center"]
                )
                # Map to ORM
                dept = models.Department(
                    department_id=int(row["department_id"]),
                    name=schema.name,
                    description=schema.description,
                    cost_center=schema.cost_center
                )
                session.merge(dept)
        session.flush()

    # 2. Seed Employees
    emp_file = os.path.join(data_dir, "employees.csv")
    if os.path.exists(emp_file):
        print("Seeding employees...")
        with open(emp_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Map fields & validate
                schema = schemas.EmployeeCreate(
                    full_name=row["full_name"],
                    email=row["email"],
                    phone=row["phone"],
                    department_id=int(row["department_id"]),
                    manager_id=parse_nullable_int(row["manager_id"]),
                    salary=float(row["salary"]),
                    joining_date=parse_date(row["joining_date"]),
                    location=row["location"],
                    status=row["status"]
                )
                emp = models.Employee(
                    employee_id=int(row["employee_id"]),
                    full_name=schema.full_name,
                    email=schema.email,
                    phone=schema.phone,
                    department_id=schema.department_id,
                    manager_id=schema.manager_id,
                    salary=schema.salary,
                    joining_date=schema.joining_date,
                    location=schema.location,
                    status=schema.status
                )
                session.merge(emp)
        session.flush()

    # 3. Seed Users
    user_file = os.path.join(data_dir, "users.csv")
    if os.path.exists(user_file):
        print("Seeding users...")
        with open(user_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                schema = schemas.UserCreate(
                    employee_id=int(row["employee_id"]),
                    username=row["username"],
                    password_hash=row["password_hash"],
                    role=row["role"],
                    is_active=row["is_active"].lower() in ("true", "1")
                )
                user = models.User(
                    user_id=int(row["user_id"]),
                    employee_id=schema.employee_id,
                    username=schema.username,
                    password_hash=schema.password_hash,
                    role=schema.role,
                    is_active=schema.is_active
                )
                session.merge(user)
        session.flush()

    # 4. Seed Customers
    cust_file = os.path.join(data_dir, "customers.csv")
    if os.path.exists(cust_file):
        print("Seeding customers...")
        with open(cust_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                schema = schemas.CustomerCreate(
                    company_name=row["company_name"],
                    contact_name=row["contact_name"],
                    email=row["email"],
                    phone=row["phone"],
                    country=row["country"],
                    industry=row["industry"]
                )
                cust = models.Customer(
                    customer_id=int(row["customer_id"]),
                    company_name=schema.company_name,
                    contact_name=schema.contact_name,
                    email=schema.email,
                    phone=schema.phone,
                    country=schema.country,
                    industry=schema.industry
                )
                session.merge(cust)
        session.flush()

    # 5. Seed Products
    prod_file = os.path.join(data_dir, "products.csv")
    if os.path.exists(prod_file):
        print("Seeding products...")
        with open(prod_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                schema = schemas.ProductCreate(
                    name=row["name"],
                    category=row["category"],
                    price=float(row["price"]),
                    supplier=row["supplier"],
                    stock=int(row["stock"])
                )
                prod = models.Product(
                    product_id=int(row["product_id"]),
                    name=schema.name,
                    category=schema.category,
                    price=schema.price,
                    supplier=schema.supplier,
                    stock=schema.stock
                )
                session.merge(prod)
        session.flush()

    # 6. Seed Inventory
    inv_file = os.path.join(data_dir, "inventory.csv")
    if os.path.exists(inv_file):
        print("Seeding inventory...")
        with open(inv_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                schema = schemas.InventoryCreate(
                    product_id=int(row["product_id"]),
                    warehouse_location=row["warehouse_location"],
                    quantity_on_hand=int(row["quantity_on_hand"]),
                    safety_stock=int(row["safety_stock"]),
                    reorder_point=int(row["reorder_point"]),
                    last_restocked=parse_date(row["last_restocked"])
                )
                inv = models.Inventory(
                    inventory_id=int(row["inventory_id"]),
                    product_id=schema.product_id,
                    warehouse_location=schema.warehouse_location,
                    quantity_on_hand=schema.quantity_on_hand,
                    safety_stock=schema.safety_stock,
                    reorder_point=schema.reorder_point,
                    last_restocked=schema.last_restocked
                )
                session.merge(inv)
        session.flush()

    # 7. Seed Orders
    order_file = os.path.join(data_dir, "orders.csv")
    if os.path.exists(order_file):
        print("Seeding orders...")
        with open(order_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                schema = schemas.OrderCreate(
                    customer_id=int(row["customer_id"]),
                    product_id=int(row["product_id"]),
                    quantity=int(row["quantity"]),
                    price=float(row["price"]),
                    discount=float(row["discount"]),
                    status=row["status"],
                    order_date=parse_date(row["order_date"])
                )
                order = models.Order(
                    order_id=int(row["order_id"]),
                    customer_id=schema.customer_id,
                    product_id=schema.product_id,
                    quantity=schema.quantity,
                    price=schema.price,
                    discount=schema.discount,
                    status=schema.status,
                    order_date=schema.order_date
                )
                session.merge(order)
        session.flush()

    # 8. Seed Support Tickets
    ticket_file = os.path.join(data_dir, "support_tickets.csv")
    if os.path.exists(ticket_file):
        print("Seeding support tickets...")
        with open(ticket_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                schema = schemas.SupportTicketCreate(
                    customer_id=int(row["customer_id"]),
                    issue=row["issue"],
                    priority=row["priority"],
                    assigned_employee_id=parse_nullable_int(row["assigned_employee_id"]),
                    status=row["status"],
                    created_date=parse_date(row["created_date"]),
                    resolved_date=parse_date(row["resolved_date"])
                )
                ticket = models.SupportTicket(
                    ticket_id=int(row["ticket_id"]),
                    customer_id=schema.customer_id,
                    issue=schema.issue,
                    priority=schema.priority,
                    assigned_employee_id=schema.assigned_employee_id,
                    status=schema.status,
                    created_date=schema.created_date,
                    resolved_date=schema.resolved_date
                )
                session.merge(ticket)
        session.flush()

    print("Seeding completed successfully!")
