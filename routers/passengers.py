from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Passenger
from schemas import PassengerCreate, PassengerUpdate, PassengerResponse

router = APIRouter(prefix="/api/passengers", tags=["passengers"])


@router.get("/", response_model=List[PassengerResponse])
def get_passengers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of all passengers"""
    passengers = db.query(Passenger).offset(skip).limit(limit).all()
    return passengers


@router.get("/{passenger_id}", response_model=PassengerResponse)
def get_passenger(passenger_id: int, db: Session = Depends(get_db)):
    """Get specific passenger by ID"""
    passenger = db.query(Passenger).filter(Passenger.id == passenger_id).first()
    if not passenger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Passenger with id {passenger_id} not found"
        )
    return passenger


@router.post("/", response_model=PassengerResponse, status_code=status.HTTP_201_CREATED)
def create_passenger(passenger: PassengerCreate, db: Session = Depends(get_db)):
    """Register a new passenger"""
    # Check if phone already exists
    existing = db.query(Passenger).filter(Passenger.phone == passenger.phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # Check if email already exists
    existing = db.query(Passenger).filter(Passenger.email == passenger.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    db_passenger = Passenger(**passenger.dict())
    db.add(db_passenger)
    db.commit()
    db.refresh(db_passenger)
    return db_passenger


@router.put("/{passenger_id}", response_model=PassengerResponse)
def update_passenger(
    passenger_id: int,
    passenger_update: PassengerUpdate,
    db: Session = Depends(get_db)
):
    """Update passenger information"""
    passenger = db.query(Passenger).filter(Passenger.id == passenger_id).first()
    if not passenger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Passenger with id {passenger_id} not found"
        )
    
    update_data = passenger_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(passenger, field, value)
    
    db.commit()
    db.refresh(passenger)
    return passenger


@router.delete("/{passenger_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_passenger(passenger_id: int, db: Session = Depends(get_db)):
    """Delete a passenger account"""
    passenger = db.query(Passenger).filter(Passenger.id == passenger_id).first()
    if not passenger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Passenger with id {passenger_id} not found"
        )
    
    db.delete(passenger)
    db.commit()
    return None
