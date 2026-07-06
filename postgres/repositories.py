from typing import Generic, TypeVar, Type, List, Optional, Any
from sqlalchemy.orm import Session
from .database import Base
from . import models

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic Base Repository outlining clean CRUD patterns.
    """
    def __init__(self, model: Type[ModelType], session: Session):
        self.model = model
        self.session = session

    def get(self, id: Any) -> Optional[ModelType]:
        return self.session.get(self.model, id)

    def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.session.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: Any) -> ModelType:
        # Accept pydantic schema or dict, using v2 model_dump if available
        if hasattr(obj_in, "model_dump"):
            data = obj_in.model_dump()
        elif hasattr(obj_in, "dict"):
            data = obj_in.dict()
        else:
            data = obj_in
            
        db_obj = self.model(**data)
        self.session.add(db_obj)
        self.session.flush()  # Populates ID but does not commit
        return db_obj

    def update(self, db_obj: ModelType, obj_in: Any) -> ModelType:
        if hasattr(obj_in, "model_dump"):
            update_data = obj_in.model_dump(exclude_unset=True)
        elif hasattr(obj_in, "dict"):
            update_data = obj_in.dict(exclude_unset=True)
        else:
            update_data = obj_in
            
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        self.session.add(db_obj)
        self.session.flush()
        return db_obj

    def delete(self, id: Any) -> Optional[ModelType]:
        obj = self.get(id)
        if obj:
            self.session.delete(obj)
            self.session.flush()
        return obj


class DepartmentRepository(BaseRepository[models.Department]):
    def __init__(self, session: Session):
        super().__init__(models.Department, session)

    def get_by_name(self, name: str) -> Optional[models.Department]:
        return self.session.query(models.Department).filter(models.Department.name == name).first()


class EmployeeRepository(BaseRepository[models.Employee]):
    def __init__(self, session: Session):
        super().__init__(models.Employee, session)

    def get_by_email(self, email: str) -> Optional[models.Employee]:
        return self.session.query(models.Employee).filter(models.Employee.email == email).first()


class UserRepository(BaseRepository[models.User]):
    def __init__(self, session: Session):
        super().__init__(models.User, session)

    def get_by_username(self, username: str) -> Optional[models.User]:
        return self.session.query(models.User).filter(models.User.username == username).first()


class CustomerRepository(BaseRepository[models.Customer]):
    def __init__(self, session: Session):
        super().__init__(models.Customer, session)

    def get_by_company_name(self, company_name: str) -> Optional[models.Customer]:
        return self.session.query(models.Customer).filter(models.Customer.company_name == company_name).first()


class ProductRepository(BaseRepository[models.Product]):
    def __init__(self, session: Session):
        super().__init__(models.Product, session)

    def get_by_name(self, name: str) -> Optional[models.Product]:
        return self.session.query(models.Product).filter(models.Product.name == name).first()


class InventoryRepository(BaseRepository[models.Inventory]):
    def __init__(self, session: Session):
        super().__init__(models.Inventory, session)

    def get_by_product(self, product_id: int) -> Optional[models.Inventory]:
        return self.session.query(models.Inventory).filter(models.Inventory.product_id == product_id).first()


class OrderRepository(BaseRepository[models.Order]):
    def __init__(self, session: Session):
        super().__init__(models.Order, session)

    def list_by_customer(self, customer_id: int) -> List[models.Order]:
        return self.session.query(models.Order).filter(models.Order.customer_id == customer_id).all()


class SupportTicketRepository(BaseRepository[models.SupportTicket]):
    def __init__(self, session: Session):
        super().__init__(models.SupportTicket, session)

    def list_by_status(self, status: str) -> List[models.SupportTicket]:
        return self.session.query(models.SupportTicket).filter(models.SupportTicket.status == status).all()
