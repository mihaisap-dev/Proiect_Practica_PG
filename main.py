import os
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

from models import (
    SessionLocal, Identifiers, Countries, ConsumerUnits, 
    Ownership, Relationships, Characteristics, IdentifierCharacteristics
)

class IdentifierSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    identifier_name: str
    description: Optional[str]
    identifier_type: str

class CountrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    iso_code: str
    short_code: str

class ConsumerUnitSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    number_of_consumers: int
    country_name: str

class OwnershipSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    identifier_name: str
    user_id_tnumber: str
    originator_first_name: Optional[str]
    originator_last_name: Optional[str]
    email: Optional[str]
    owner_first_name: Optional[str]
    owner_last_name: Optional[str]

class RelationshipSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    from_identifier_name: str
    to_identifier_name: str
    relationship_name: str

class CharacteristicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    master_name: str
    name: str
    specifics: Optional[str]
    target: Optional[float]
    lower_limit: Optional[float]
    upper_limit: Optional[float]
    engineering_unit: Optional[str]

class QualityCheckRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    identifier_name: str
    master_name: str
    characteristic_name: str
    measured_value: float

app = FastAPI(title="Sistem ERP Productie & Calitate")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/identifiers", response_model=List[IdentifierSchema], tags=["Productie"])
def get_identifiers(db: Session = Depends(get_db)):
    return db.query(Identifiers).all()

@app.get("/countries", response_model=List[CountrySchema], tags=["Logistica"])
def get_countries(db: Session = Depends(get_db)):
    return db.query(Countries).all()

@app.get("/consumer-units", response_model=List[ConsumerUnitSchema], tags=["Logistica"])
def get_consumer_units(db: Session = Depends(get_db)):
    return db.query(ConsumerUnits).all()

@app.get("/ownership", response_model=List[OwnershipSchema], tags=["Administrare"])
def get_ownership(db: Session = Depends(get_db)):
    return db.query(Ownership).all()

@app.get("/relationships", response_model=List[RelationshipSchema], tags=["Productie"])
def get_relationships(db: Session = Depends(get_db)):
    return db.query(Relationships).all()

@app.get("/characteristics", response_model=List[CharacteristicSchema], tags=["Calitate"])
def get_characteristics(db: Session = Depends(get_db)):
    return db.query(Characteristics).all()

@app.post("/identifiers", response_model=IdentifierSchema, tags=["Productie"])
def create_identifier(data: IdentifierSchema, db: Session = Depends(get_db), x_username: str = Header(None)):
    # Verificare securitate (opțional, dar recomandat)
    if x_username != os.environ.get("USERNAME", "admin_pg"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    new_prod = Identifiers(
        identifier_name=data.identifier_name,
        description=data.description,
        identifier_type=data.identifier_type
    )
    db.add(new_prod)
    db.commit()
    db.refresh(new_prod)
    return new_prod

@app.delete("/identifiers/{name}", tags=["Productie"])
def delete_identifier(name: str, db: Session = Depends(get_db), x_username: str = Header(None)):
    if x_username != os.environ.get("USERNAME", "admin_pg"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    prod = db.query(Identifiers).filter(Identifiers.identifier_name == name).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Produsul nu a fost găsit.")
    
    db.delete(prod)
    db.commit()
    return {"message": f"Produsul {name} a fost șters cu succes."}

@app.post("/validate-quality", tags=["Calitate"])
def validate_quality(data: QualityCheckRequest, db: Session = Depends(get_db), x_username: str = Header(None)):
    expected_username = os.environ.get("USERNAME", "admin_pg")

    if x_username != expected_username:
        raise HTTPException(status_code=401, detail="Unauthorized")

    spec = db.query(Characteristics).filter(
        Characteristics.master_name == data.master_name,
        Characteristics.name == data.characteristic_name
    ).first()

    if not spec:
        raise HTTPException(status_code=404, detail="Specificatia nu exista in baza de date.")

    is_ok = True
    msg = "Produs conform."

    if spec.lower_limit is not None and data.measured_value < spec.lower_limit:
        is_ok = False
        msg = f"Eroare: Valoare prea mica. Minim acceptat: {spec.lower_limit}"
    elif spec.upper_limit is not None and data.measured_value > spec.upper_limit:
        is_ok = False
        msg = f"Eroare: Valoare prea mare. Maxim acceptat: {spec.upper_limit}"

    return {
        "decizie": "ACCEPTAT" if is_ok else "RESPINS",
        "detalii": msg,
        "produs": data.identifier_name,
        "parametru": data.characteristic_name,
        "valoare": data.measured_value,
        "unitate": spec.engineering_unit
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)