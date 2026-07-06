import re
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# ----------------------------------------------------
# 1. Department Schemas
# ----------------------------------------------------
class DepartmentBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    cost_center: str = Field(..., max_length=50)

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    department_id: int

    class Config:
        from_attributes = True


# ----------------------------------------------------
# 2. Employee Schemas
# ----------------------------------------------------
class EmployeeBase(BaseModel):
    full_name: str = Field(..., max_length=100)
    email: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=50)
    department_id: int
    manager_id: Optional[int] = None
    salary: float = Field(..., gt=0)
    joining_date: date
    location: str = Field(..., max_length=100)
    status: str = Field(..., max_length=50)

    @field_validator("email")
    @classmethod
    def validate_email_pattern(cls, v: str) -> str:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"Active", "On Leave", "Terminated"}
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    employee_id: int

    class Config:
        from_attributes = True


# ----------------------------------------------------
# 3. User Schemas
# ----------------------------------------------------
class UserBase(BaseModel):
    employee_id: int
    username: str = Field(..., max_length=50)
    role: str = Field(..., max_length=50)
    is_active: bool = True

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        allowed = {"Admin", "Manager", "User"}
        if v not in allowed:
            raise ValueError(f"Role must be one of {allowed}")
        return v

class UserCreate(UserBase):
    password_hash: str = Field(..., max_length=255)

class UserResponse(UserBase):
    user_id: int

    class Config:
        from_attributes = True


# ----------------------------------------------------
# 4. Customer Schemas
# ----------------------------------------------------
class CustomerBase(BaseModel):
    company_name: str = Field(..., max_length=150)
    contact_name: str = Field(..., max_length=100)
    email: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=50)
    country: str = Field(..., max_length=100)
    industry: str = Field(..., max_length=100)

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    customer_id: int

    class Config:
        from_attributes = True


# ----------------------------------------------------
# 5. Product Schemas
# ----------------------------------------------------
class ProductBase(BaseModel):
    name: str = Field(..., max_length=100)
    category: str = Field(..., max_length=50)
    price: float = Field(..., ge=0)
    supplier: str = Field(..., max_length=100)
    stock: int = Field(..., ge=0)

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    product_id: int

    class Config:
        from_attributes = True


# ----------------------------------------------------
# 6. Inventory Schemas
# ----------------------------------------------------
class InventoryBase(BaseModel):
    product_id: int
    warehouse_location: str = Field(..., max_length=100)
    quantity_on_hand: int = Field(..., ge=0)
    safety_stock: int = Field(0, ge=0)
    reorder_point: int = Field(0, ge=0)
    last_restocked: Optional[date] = None

class InventoryCreate(InventoryBase):
    pass

class InventoryResponse(InventoryBase):
    inventory_id: int

    class Config:
        from_attributes = True


# ----------------------------------------------------
# 7. Order Schemas
# ----------------------------------------------------
class OrderBase(BaseModel):
    customer_id: int
    product_id: int
    quantity: int = Field(..., gt=0)
    price: float = Field(..., ge=0)
    discount: float = Field(0.00, ge=0.00, le=1.00)
    status: str = Field(..., max_length=50)
    order_date: date

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"Pending", "Shipped", "Delivered", "Cancelled"}
        if v not in allowed:
            raise ValueError(f"Order status must be one of {allowed}")
        return v

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    order_id: int

    class Config:
        from_attributes = True


# ----------------------------------------------------
# 8. Support Ticket Schemas
# ----------------------------------------------------
class SupportTicketBase(BaseModel):
    customer_id: int
    issue: str
    priority: str = Field(..., max_length=50)
    assigned_employee_id: Optional[int] = None
    status: str = Field(..., max_length=50)
    created_date: date
    resolved_date: Optional[date] = None

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        allowed = {"Low", "Medium", "High", "Critical"}
        if v not in allowed:
            raise ValueError(f"Priority must be one of {allowed}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = {"Open", "In Progress", "Resolved", "Closed"}
        if v not in allowed:
            raise ValueError(f"Ticket status must be one of {allowed}")
        return v

class SupportTicketCreate(SupportTicketBase):
    pass

class SupportTicketResponse(SupportTicketBase):
    ticket_id: int

    class Config:
        from_attributes = True
