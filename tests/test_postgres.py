import os
import sys
import unittest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set paths
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)

from postgres.database import Base
from postgres import models
from postgres import schemas
from postgres.repositories import DepartmentRepository, EmployeeRepository
from postgres.service import seed_db_from_csv


class TestPostgreSQLIntegration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Create an in-memory SQLite database for fast, offline ORM validation
        cls.engine = create_engine("sqlite:///:memory:")
        cls.SessionLocal = sessionmaker(bind=cls.engine)
        Base.metadata.create_all(bind=cls.engine)

    def setUp(self):
        # Refresh connection session
        self.session = self.SessionLocal()

    def tearDown(self):
        # Clear changes and close
        self.session.rollback()
        self.session.close()

    def test_department_crud(self):
        """Verify basic create, read, and delete operations on Departments."""
        repo = DepartmentRepository(self.session)
        
        # Create
        dept_in = schemas.DepartmentCreate(
            name="Research & Development",
            description="Enterprise R&D division",
            cost_center="CC-909"
        )
        dept = repo.create(dept_in)
        self.session.commit()
        
        # Read
        retrieved = repo.get(dept.department_id)
        self.assertEqual(retrieved.name, "Research & Development")
        self.assertEqual(retrieved.cost_center, "CC-909")
        
        # Query by name
        retrieved_by_name = repo.get_by_name("Research & Development")
        self.assertIsNotNone(retrieved_by_name)
        
        # Delete
        repo.delete(dept.department_id)
        self.session.commit()
        self.assertIsNone(repo.get(dept.department_id))

    def test_employee_pydantic_validation(self):
        """Verify that invalid inputs raise appropriate validation errors."""
        # 1. Invalid email
        with self.assertRaises(ValueError) as ctx:
            schemas.EmployeeCreate(
                full_name="John Doe",
                email="invalid_email_format",
                phone="+1-555-1234",
                department_id=1,
                salary=80000.0,
                joining_date=date(2025, 1, 1),
                location="Bengaluru",
                status="Active"
            )
        self.assertIn("Invalid email format", str(ctx.exception))

        # 2. Invalid status
        with self.assertRaises(ValueError) as ctx:
            schemas.EmployeeCreate(
                full_name="John Doe",
                email="john.doe@novatech.com",
                phone="+1-555-1234",
                department_id=1,
                salary=80000.0,
                joining_date=date(2025, 1, 1),
                location="Bengaluru",
                status="NonExistentStatus"
            )
        self.assertIn("Status must be one of", str(ctx.exception))

        # 3. Invalid salary (gt=0)
        with self.assertRaises(ValueError) as ctx:
            schemas.EmployeeCreate(
                full_name="John Doe",
                email="john.doe@novatech.com",
                phone="+1-555-1234",
                department_id=1,
                salary=-500.0,
                joining_date=date(2025, 1, 1),
                location="Bengaluru",
                status="Active"
            )
        self.assertIn("Input should be greater than 0", str(ctx.exception))

    def test_transactional_rollback(self):
        """Confirm that if an exception is raised inside a transaction block, changes are rolled back."""
        # Insert a valid department
        repo = DepartmentRepository(self.session)
        dept_in = schemas.DepartmentCreate(
            name="Operations Unit",
            description="Core logistics ops",
            cost_center="CC-999"
        )
        repo.create(dept_in)
        self.session.flush()
        
        # Verify it exists in current session
        self.assertIsNotNone(repo.get_by_name("Operations Unit"))
        
        # Roll back explicitly to simulate transactional failure
        self.session.rollback()
        
        # Verify it no longer exists
        self.assertIsNone(repo.get_by_name("Operations Unit"))

    def test_csv_seeding_pipeline(self):
        """
        Runs the full CSV parsing pipeline on the SQLite database to verify
        that all generated CSV file records load without validation errors.
        """
        # Run seeding against our database instance using real data/database folder path
        csv_dir = os.path.join(root_dir, "data", "database")
        
        # Create a clean SQLite database to ensure clean seeding comparison
        engine_clean = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine_clean)
        SessionClean = sessionmaker(bind=engine_clean)
        session_clean = SessionClean()
        
        try:
            seed_db_from_csv(session_clean, csv_dir)
            session_clean.commit()
            
            # Verify departments loaded (should be 6)
            depts_count = session_clean.query(models.Department).count()
            self.assertEqual(depts_count, 6)
            
            # Verify employees loaded (should be 50)
            emps_count = session_clean.query(models.Employee).count()
            self.assertEqual(emps_count, 50)
            
            # Verify orders loaded (should be 500)
            orders_count = session_clean.query(models.Order).count()
            self.assertEqual(orders_count, 500)
            
        finally:
            session_clean.close()


if __name__ == "__main__":
    unittest.main()
