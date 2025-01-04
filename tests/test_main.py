import unittest
from fastapi.testclient import TestClient
from main import app, Base, Termeles, DwarfsAsWorkers, DatabaseHandler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestApp(unittest.TestCase):
    """
    Unit tests for the FastAPI application endpoints and database operations.
    """
    @classmethod
    def setUpClass(cls):
        """Set up the database and test client before all tests"""
        cls.client = TestClient(app)
    def setUp(self):
        """Initialize a new database session before each test."""
        self.test_db_url = 'sqlite:///:memory:'
        self.engine = create_engine(self.test_db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.my_session = sessionmaker(bind=self.engine)
        self.db_handler = DatabaseHandler(db_url=self.test_db_url)

    def tearDown(self):
        """Rollback and close the session after each test."""
        Base.metadata.drop_all(self.engine)

    def test_insert_termeles(self):
        """Insert correct test data"""
        self.db_handler.insert_termeles("2025-01-03", 3, 3, 0.1)
        session = self.db_handler.my_session()
        result = session.query(Termeles).order_by(Termeles.id.desc()).first()
        session.close()
        self.assertIsNotNone(result)

    def test_insert_dwarf_as_worker(self):
        """Insert correct test data"""
        self.db_handler.insert_dwarf_as_worker("Hapci", "2025-01-03", 1, 1, 0.1)
        session = self.db_handler.my_session()
        result = session.query(DwarfsAsWorkers).order_by(DwarfsAsWorkers.id.desc()).first()
        session.close()
        self.assertIsNotNone(result)

    def test_submit_production_data(self):
        """
        Test inserting valid production data.
        :return:
        """
        response = self.client.post(
            "/submit",
            data={
                "datum": "2025-01-04",
                "arany": 1,
                "ezust": 2,
                "gyemant": 0.5
            },
        )

        self.assertEqual(response.status_code, 200)

    def test_submit_dwarf_data(self):
        """
        Test inserting valid dwarf data.
        """
        response = self.client.post(
            "/submit-dwarf",
            data={
                "name": "Kuka",
                "datum": "2025-01-04",
                "gold": 1,
                "silver": 2,
                "diamond": 0.5
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_submit_missing_field(self):
        """Test missing fields."""
        response = self.client.post(
            "/submit",
            data={
                "datum": "2025-01-04",
                "arany": 1,
                "ezust": 2,
                # 'gyemant' is missing
            },
        )
        self.assertEqual(response.status_code, 422)  # Invalid request

    def test_submit_negative_values(self):
        """Test negative values in production data."""
        response = self.client.post(
            "/submit",
            data={
                "datum": "2025-01-03",
                "arany": -1,  # Invalid negative value
                "ezust": 2,
                "gyemant": 0.5
            },
        )
        self.assertEqual(response.status_code, 500)

    def test_submit_dwarf_negative_values(self):
        """Test negative values in dwarf data."""
        response = self.client.post(
            "/submit-dwarf",
            data={
                "name": "Szundi",
                "datum": "2025-01-03",
                "gold": -1,  # Invalid negative value
                "silver": 2,
                "diamond": 0.5
            },
        )
        self.assertEqual(response.status_code, 500)

    def test_submit_dwarf_invalid_date(self):
        """Test invalid date format for dwarf data."""
        response = self.client.post(
            "/submit-dwarf",
            data={
                "name": "Morgó",
                "datum": "03-01-2025",  # Invalid format
                "gold": 1,
                "silver": 2,
                "diamond": 0.5
            },
        )
        self.assertEqual(response.status_code, 500)

    def test_submit_dwarf_missing_field(self):
        """Test missing field for dwarf data."""
        response = self.client.post(
            "/submit-dwarf",
            data={
                "name": "Vidor",
                "datum": "2025-01-03",
                "gold": 1,
                "silver": 2
                # 'diamond' is missing
            },
        )
        self.assertEqual(response.status_code, 422)

if __name__ == "__main__":
    unittest.main()
