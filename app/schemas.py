from pydantic import BaseModel, ConfigDict, Field, validator
from typing import List, Optional

class ActivityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[int] = None


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(ActivityBase):
    pass


class Activity(ActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    level: int
    children: List['Activity'] = []
    organizations_count: Optional[int] = None


class BuildingBase(BaseModel):
    address: str = Field(..., min_length=1, max_length=500)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    description: Optional[str] = None


class BuildingCreate(BuildingBase):
    pass


class BuildingUpdate(BuildingBase):
    pass


class Building(BuildingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organizations_count: Optional[int] = None


class PhoneBase(BaseModel):
    number: str = Field(..., min_length=1, max_length=50)


class PhoneCreate(PhoneBase):
    organization_id: int


class Phone(PhoneBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int


class OrganizationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    building_id: Optional[int] = None


class OrganizationCreate(OrganizationBase):
    phone_numbers: Optional[List[str]] = []
    activity_ids: Optional[List[int]] = []


class OrganizationUpdate(OrganizationBase):
    phone_numbers: Optional[List[str]] = None
    activity_ids: Optional[List[int]] = None


class Organization(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: int
    updated_at: int
    building: Optional[Building] = None
    activities: List[Activity] = []
    phones: List[Phone] = []


class OrganizationSearch(BaseModel):
    name: Optional[str] = None
    activity_name: Optional[str] = None
    building_address: Optional[str] = None


class GeoSearch(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius: float = Field(1000, gt=0)


class RectangleSearch(BaseModel):
    min_lat: float = Field(..., ge=-90, le=90)
    max_lat: float = Field(..., ge=-90, le=90)
    min_lon: float = Field(..., ge=-180, le=180)
    max_lon: float = Field(..., ge=-180, le=180)

    @validator('max_lat')
    def validate_lat_range(cls, v, values):
        if 'min_lat' in values and v <= values['min_lat']:
            raise ValueError('max_lat must be greater than min_lat')
        return v

    @validator('max_lon')
    def validate_lon_range(cls, v, values):
        if 'min_lon' in values and v <= values['min_lon']:
            raise ValueError('max_lon must be greater than min_lon')
        return v


Activity.model_rebuild()