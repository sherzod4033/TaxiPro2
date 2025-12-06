from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from models import DriverStatus, TripStatus


# Driver Schemas
class DriverBase(BaseModel):
    name: str
    phone: str
    license_number: str
    car_model: str
    car_number: str


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    car_model: Optional[str] = None
    car_number: Optional[str] = None


class DriverStatusUpdate(BaseModel):
    status: DriverStatus


class DriverResponse(DriverBase):
    id: int
    rating: float
    status: DriverStatus
    created_at: datetime

    class Config:
        from_attributes = True


# Passenger Schemas
class PassengerBase(BaseModel):
    name: str
    phone: str
    email: EmailStr


class PassengerCreate(PassengerBase):
    pass


class PassengerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class PassengerResponse(PassengerBase):
    id: int
    rating: float
    created_at: datetime

    class Config:
        from_attributes = True


# Trip Schemas
class TripBase(BaseModel):
    pickup_location: str
    dropoff_location: str


class TripCreate(TripBase):
    passenger_id: int


class TripUpdate(BaseModel):
    distance: Optional[float] = None
    price: Optional[float] = None


class TripStatusUpdate(BaseModel):
    status: TripStatus
    driver_id: Optional[int] = None


class TripResponse(TripBase):
    id: int
    passenger_id: int
    driver_id: Optional[int]
    distance: Optional[float]
    price: Optional[float]
    status: TripStatus
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
