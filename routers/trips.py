from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database import get_db
from models import Trip, Driver, Passenger, TripStatus, DriverStatus
from schemas import TripCreate, TripUpdate, TripResponse, TripStatusUpdate

router = APIRouter(prefix="/api/trips", tags=["trips"])


@router.get("/", response_model=List[TripResponse])
def get_trips(
    status: Optional[TripStatus] = None,
    passenger_id: Optional[int] = None,
    driver_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of trips with optional filters"""
    query = db.query(Trip)
    
    if status:
        query = query.filter(Trip.status == status)
    if passenger_id:
        query = query.filter(Trip.passenger_id == passenger_id)
    if driver_id:
        query = query.filter(Trip.driver_id == driver_id)
    
    trips = query.order_by(Trip.created_at.desc()).offset(skip).limit(limit).all()
    return trips


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    """Get specific trip by ID"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with id {trip_id} not found"
        )
    return trip


@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(trip: TripCreate, db: Session = Depends(get_db)):
    """Create a new trip request"""
    # Verify passenger exists
    passenger = db.query(Passenger).filter(Passenger.id == trip.passenger_id).first()
    if not passenger:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Passenger with id {trip.passenger_id} not found"
        )
    
    # Calculate estimated price (simple calculation: 50 rubles base + random)
    import random
    estimated_price = 50 + random.randint(50, 500)
    
    db_trip = Trip(
        **trip.dict(),
        price=estimated_price,
        status=TripStatus.PENDING
    )
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip


@router.patch("/{trip_id}/accept", response_model=TripResponse)
def accept_trip(trip_id: int, driver_id: int, db: Session = Depends(get_db)):
    """Driver accepts a trip"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with id {trip_id} not found"
        )
    
    if trip.status != TripStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trip is not in pending status"
        )
    
    # Verify driver exists and is available
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Driver with id {driver_id} not found"
        )
    
    if driver.status != DriverStatus.AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver is not available"
        )
    
    trip.driver_id = driver_id
    trip.status = TripStatus.ACCEPTED
    driver.status = DriverStatus.BUSY
    
    db.commit()
    db.refresh(trip)
    return trip


@router.patch("/{trip_id}/start", response_model=TripResponse)
def start_trip(trip_id: int, db: Session = Depends(get_db)):
    """Start the trip (driver picked up passenger)"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with id {trip_id} not found"
        )
    
    if trip.status != TripStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip must be accepted before starting"
        )
    
    trip.status = TripStatus.IN_PROGRESS
    db.commit()
    db.refresh(trip)
    return trip


@router.patch("/{trip_id}/complete", response_model=TripResponse)
def complete_trip(trip_id: int, distance: float, db: Session = Depends(get_db)):
    """Complete the trip"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with id {trip_id} not found"
        )
    
    if trip.status != TripStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip must be in progress to complete"
        )
    
    trip.status = TripStatus.COMPLETED
    trip.distance = distance
    trip.completed_at = datetime.utcnow()
    
    # Update driver status to available
    if trip.driver_id:
        driver = db.query(Driver).filter(Driver.id == trip.driver_id).first()
        if driver:
            driver.status = DriverStatus.AVAILABLE
    
    db.commit()
    db.refresh(trip)
    return trip


@router.patch("/{trip_id}/cancel", response_model=TripResponse)
def cancel_trip(trip_id: int, db: Session = Depends(get_db)):
    """Cancel the trip"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with id {trip_id} not found"
        )
    
    if trip.status in [TripStatus.COMPLETED, TripStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed or already cancelled trip"
        )
    
    trip.status = TripStatus.CANCELLED
    
    # Update driver status to available if assigned
    if trip.driver_id:
        driver = db.query(Driver).filter(Driver.id == trip.driver_id).first()
        if driver:
            driver.status = DriverStatus.AVAILABLE
    
    db.commit()
    db.refresh(trip)
    return trip


@router.put("/{trip_id}", response_model=TripResponse)
def update_trip(
    trip_id: int,
    trip_update: TripUpdate,
    db: Session = Depends(get_db)
):
    """Update trip details"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with id {trip_id} not found"
        )
    
    update_data = trip_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trip, field, value)
    
    db.commit()
    db.refresh(trip)
    return trip
