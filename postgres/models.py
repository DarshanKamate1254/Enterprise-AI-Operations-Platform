import sys
import os
from datetime import date
from typing import List, Optional
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import String, Text, Numeric, Date, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

# 1. Department ORM Model
class Department(Base):
    __tablename__ = "departments"

    department_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cost_center: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    # Relationships
    employees: Mapped[List["Employee"]] = relationship(back_populates="department", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Department name={self.name} cost_center={self.cost_center}>"


# 2. Employee ORM Model
class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        CheckConstraint("salary > 0", name="employees_salary_check"),
        CheckConstraint("status IN ('Active', 'On Leave', 'Terminated')", name="employees_status_check"),
    )

    employee_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.department_id", ondelete="CASCADE"), nullable=False)
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True)
    salary: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    joining_date: Mapped[date] = mapped_column(Date, nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationships
    department: Mapped["Department"] = relationship(back_populates="employees")
    manager: Mapped[Optional["Employee"]] = relationship(remote_side=[employee_id], backref="subordinates")
    user: Mapped[Optional["User"]] = relationship(back_populates="employee", uselist=False, cascade="all, delete-orphan")
    support_tickets: Mapped[List["SupportTicket"]] = relationship(back_populates="assigned_employee")

    def __repr__(self):
        return f"<Employee full_name={self.full_name} email={self.email}>"


# 3. User ORM Model
class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('Admin', 'Manager', 'User')", name="users_role_check"),
    )

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.employee_id", ondelete="CASCADE"), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    employee: Mapped["Employee"] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User username={self.username} role={self.role}>"


# 4. Customer ORM Model
class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    contact_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    industry: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    orders: Mapped[List["Order"]] = relationship(back_populates="customer", cascade="all, delete-orphan")
    support_tickets: Mapped[List["SupportTicket"]] = relationship(back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer company_name={self.company_name} contact_name={self.contact_name}>"


# 5. Product ORM Model
class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price >= 0", name="products_price_check"),
        CheckConstraint("stock >= 0", name="products_stock_check"),
    )

    product_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    supplier: Mapped[str] = mapped_column(String(100), nullable=False)
    stock: Mapped[int] = mapped_column(nullable=False)

    # Relationships
    inventory: Mapped[Optional["Inventory"]] = relationship(back_populates="product", uselist=False, cascade="all, delete-orphan")
    orders: Mapped[List["Order"]] = relationship(back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product name={self.name} price={self.price}>"


# 6. Inventory ORM Model
class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (
        CheckConstraint("quantity_on_hand >= 0", name="inventory_qty_check"),
        CheckConstraint("safety_stock >= 0", name="inventory_safety_check"),
        CheckConstraint("reorder_point >= 0", name="inventory_reorder_check"),
    )

    inventory_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id", ondelete="CASCADE"), unique=True, nullable=False)
    warehouse_location: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity_on_hand: Mapped[int] = mapped_column(nullable=False)
    safety_stock: Mapped[int] = mapped_column(nullable=False, default=0)
    reorder_point: Mapped[int] = mapped_column(nullable=False, default=0)
    last_restocked: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship(back_populates="inventory")

    def __repr__(self):
        return f"<Inventory product_id={self.product_id} warehouse_location={self.warehouse_location}>"


# 7. Order ORM Model
class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="orders_qty_check"),
        CheckConstraint("price >= 0", name="orders_price_check"),
        CheckConstraint("discount >= 0.00 AND discount <= 1.00", name="orders_discount_check"),
        CheckConstraint("status IN ('Pending', 'Shipped', 'Delivered', 'Cancelled')", name="orders_status_check"),
    )

    order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0.00)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="orders")
    product: Mapped["Product"] = relationship(back_populates="orders")

    def __repr__(self):
        return f"<Order order_id={self.order_id} status={self.status}>"


# 8. SupportTicket ORM Model
class SupportTicket(Base):
    __tablename__ = "support_tickets"
    __table_args__ = (
        CheckConstraint("priority IN ('Low', 'Medium', 'High', 'Critical')", name="tickets_priority_check"),
        CheckConstraint("status IN ('Open', 'In Progress', 'Resolved', 'Closed')", name="tickets_status_check"),
        CheckConstraint("resolved_date IS NULL OR resolved_date >= created_date", name="tickets_date_check"),
    )

    ticket_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False)
    issue: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(50), nullable=False)
    assigned_employee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.employee_id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    created_date: Mapped[date] = mapped_column(Date, nullable=False)
    resolved_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="support_tickets")
    assigned_employee: Mapped[Optional["Employee"]] = relationship(back_populates="support_tickets")

    def __repr__(self):
        return f"<SupportTicket ticket_id={self.ticket_id} priority={self.priority} status={self.status}>"
