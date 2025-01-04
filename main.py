from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, Column, String, Integer, Float, Date
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import csv
import os

# Database initialization
DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///termeles.db")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
app = FastAPI()
Base = declarative_base()

DATA_MUST_BE_POSITIVE = "Positive values are needed!"
NO_DATA = "No data found"

# Table definitions
class Termeles(Base):
    __tablename__ = 'termeles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ev = Column(Integer, nullable=False)
    honap = Column(Integer, nullable=False)
    nap = Column(Integer, nullable=False)
    aranytermeles = Column(Integer, default=0)
    ezusttermeles = Column(Integer, default=0)
    gyemanttermeles = Column(Float, default=0.0)

class DwarfsAsWorkers(Base):
    __tablename__ = 'dwarf_as_workers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    gold = Column(Integer, default=0)
    silver = Column(Integer, default=0)
    diamond = Column(Float, default=0.0)

class DatabaseHandler:
    def __init__(self, db_url='sqlite:///termeles.db'):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.my_session = sessionmaker(bind=self.engine)

    @staticmethod
    def check_value(value):
        if value < 0:
            raise ValueError(DATA_MUST_BE_POSITIVE)

    def insert_termeles(self, datum: str, arany: int, ezust: int, gyemant: float):
        session = self.my_session()
        try:
            if not isinstance(datum, str):
                raise ValueError("The 'datum' field must be a string.")
            if not isinstance(arany, int):
                raise ValueError("The 'arany' field must be an integer.")
            if not isinstance(ezust, int):
                raise ValueError("The 'ezust' field must be an integer.")
            if not isinstance(gyemant, float):
                raise ValueError("The 'gyemant' field must be a float.")

            datum_obj = datetime.strptime(datum, "%Y-%m-%d")
            ev, honap, nap = datum_obj.year, datum_obj.month, datum_obj.day

            self.check_value(arany)
            self.check_value(ezust)
            self.check_value(gyemant)

            new_record = Termeles(
                ev=ev,
                honap=honap,
                nap=nap,
                aranytermeles=arany,
                ezusttermeles=ezust,
                gyemanttermeles=gyemant
            )
            session.add(new_record)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Database error: {e}")
        except ValueError as ve:
            session.rollback()
            return {f"Validation error: {ve}"}
        finally:
            session.close()



    def insert_dwarf_as_worker(self, name: str, datum: str, gold: int, silver: int, diamond: float):
        session = self.my_session()
        try:
            if not isinstance(name, str):
                raise ValueError("The 'name' field must be a string.")
            if not isinstance(datum, str):
                raise ValueError("The 'datum' field must be a string.")
            if not isinstance(gold, int):
                raise ValueError("The 'gold' field must be an integer.")
            if not isinstance(silver, int):
                raise ValueError("The 'silver' field must be an integer.")
            if not isinstance(diamond, float):
                raise ValueError("The 'diamond' field must be a float.")
            datum_obj = datetime.strptime(datum, "%Y-%m-%d")

            new_dwarf = DwarfsAsWorkers(
                name=name,
                date=datum_obj,
                gold=gold,
                silver=silver,
                diamond=diamond
            )

            self.check_value(gold)
            self.check_value(silver)
            self.check_value(diamond)

            session.add(new_dwarf)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Database error: {e}")
        except ValueError:
            session.rollback()
            raise HTTPException(status_code=400, detail=DATA_MUST_BE_POSITIVE)
        finally:
            session.close()


@app.get("/form", response_class=HTMLResponse)
async def form_page():
    """
    Displays an HTML form for data entry.
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Adatbevitel</title>
    </head>
    <body>
        <h2>Összesített napi termelési adatok bevitele</h2>
        <form action="/submit" method="post">
            <label for="datum">Dátum (YYYY-MM-DD):</label><br>
            <input type="date" id="datum" name="datum" required><br><br>

            <label for="arany">Aranytermelés:</label><br>
            <input type="number" id="arany" name="arany" min="0" required><br><br>

            <label for="ezust">Ezüsttermelés:</label><br>
            <input type="number" id="ezust" name="ezust" min="0" required><br><br>

            <label for="gyemant">Gyémánttermelés:</label><br>
            <input type="number" id="gyemant" min="0" step="0.01" name="gyemant" required><br><br>

            <input type="submit" value="Beküldés">
        </form>
        <hr>
        <h2>Törpék egyéni napi teljesítményének rögzítése</h2>
        <form action="/submit-dwarf" method="post">
            <label for="name">Név:</label><br>
            <input type="text" id="name" name="name" required><br><br>

            <label for="datum">Dátum (YYYY-MM-DD):</label><br>
            <input type="date" id="datum" name="datum" required><br><br>

            <label for="gold">Arany:</label><br>
            <input type="number" id="gold" name="gold" min="0" required><br><br>

            <label for="silver">Ezüst:</label><br>
            <input type="number" id="silver" name="silver" min="0" required><br><br>

            <label for="diamond">Gyémánt:</label><br>
            <input type="number" id="diamond" min="0" step="0.01" name="diamond" required><br><br>

            <input type="submit" value="Beküldés">
        </form>
        <hr>
        <h2>Adatok exportálása CSV-be</h2>
        <form action="/export-csv-termeles" method="get">
            <input type="submit" value="Export Össztermelés CSV">
        </form>
        <form action="/export-csv-dwarf" method="get">
            <input type="submit" value="Export Egyéni Termelés CSV">
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/submit")
async def submit_data(
        datum: str = Form(...),
        arany: int = Form(...),
        ezust: int = Form(...),
        gyemant: float = Form(...)
):
    db_handler = DatabaseHandler()
    try:
        db_handler.insert_termeles(datum, arany, ezust, gyemant)

        if arany < 0 or ezust < 0 or gyemant < 0:
            raise HTTPException(status_code=500, detail=DATA_MUST_BE_POSITIVE)
        return {"message": "Data inserted successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/submit-dwarf")
async def submit_dwarf(
        name: str = Form(...),
        datum: str = Form(...),
        gold: int = Form(...),
        silver: int = Form(...),
        diamond: float = Form(...)
):
    db_handler = DatabaseHandler()
    try:
        db_handler.insert_dwarf_as_worker(name, datum, gold, silver, diamond)
        db_handler.check_value(gold)
        db_handler.check_value(silver)
        db_handler.check_value(diamond)
        if gold < 0 or silver < 0 or diamond < 0:
            raise HTTPException(status_code=500, detail=DATA_MUST_BE_POSITIVE)
        return {"message": "Dwarf data inserted successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/query_last_production_data")
async def query_production_data():
    session = SessionLocal()
    try:
        record = session.query(Termeles).order_by(Termeles.id.desc()).first()
        if not record:
            raise HTTPException(status_code=404, detail=NO_DATA)
        return {
            "arany": record.aranytermeles,
            "ezust": record.ezusttermeles,
            "gyemant": record.gyemanttermeles,
        }
    finally:
        session.close()

@app.get("/query_latest_dwarf_data")
async def query_dwarf_data():
    session = SessionLocal()
    try:
        record = session.query(DwarfsAsWorkers).order_by(DwarfsAsWorkers.id.desc()).first()
        if not record:
            raise HTTPException(status_code=404, detail=NO_DATA)
        return {
            "gold": record.gold,
            "silver": record.silver,
            "diamond": record.diamond,
        }
    finally:
        session.close()

@app.get("/export-csv-termeles")
async def export_csv_termeles():
    """
    Export data from the 'termeles' table to a CSV file.
    """
    session = SessionLocal()
    try:
        records = session.query(Termeles).all()
        if not records:
            raise HTTPException(status_code=404, detail=NO_DATA)

        file_path = "ossztermeles_export.csv"
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Év", "Hónap", "Nap", "Aranytermelés", "Ezüsttermelés", "Gyémánttermelés"])
            for record in records:
                writer.writerow([record.id, record.ev, record.honap, record.nap, record.aranytermeles, record.ezusttermeles, record.gyemanttermeles])
        return FileResponse(file_path, filename="ossztermeles_export.csv")
    finally:
        session.close()

@app.get("/export-csv-dwarf")
async def export_csv_dwarf():
    """
    Export data from the 'dwarf_as_workers' table to a CSV file.
    """
    session = SessionLocal()
    try:
        records = session.query(DwarfsAsWorkers).all()
        if not records:
            raise HTTPException(status_code=404, detail=NO_DATA)

        file_path = "egyeni_termeles_export.csv"
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Name", "Date", "Gold", "Silver", "Diamond"])
            for record in records:
                writer.writerow([record.id, record.name, record.date, record.gold, record.silver, record.diamond])
        return FileResponse(file_path, filename="egyeni_termeles_export.csv")
    finally:
        session.close()

