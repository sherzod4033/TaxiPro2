from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class DriverStatus(str, enum.Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"


class TripStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    license_number = Column(String, unique=True, nullable=False)
    car_model = Column(String, nullable=False)
    car_number = Column(String, unique=True, nullable=False)
    rating = Column(Float, default=5.0)
    status = Column(SQLEnum(DriverStatus), default=DriverStatus.OFFLINE)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    trips = relationship("Trip", back_populates="driver")


class Passenger(Base):
    __tablename__ = "passengers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    rating = Column(Float, default=5.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    trips = relationship("Trip", back_populates="passenger")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    passenger_id = Column(Integer, ForeignKey("passengers.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)
    pickup_location = Column(String, nullable=False)
    dropoff_location = Column(String, nullable=False)
    distance = Column(Float, nullable=True)
    price = Column(Float, nullable=True)
    status = Column(SQLEnum(TripStatus), default=TripStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    passenger = relationship("Passenger", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")
