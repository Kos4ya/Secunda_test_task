import time
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, Text, CheckConstraint
from sqlalchemy.orm import relationship
from app.database import Base

organization_activity = Table(
    'organization_activity',
    Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id', ondelete="CASCADE")),
    Column('activity_id', Integer, ForeignKey('activities.id', ondelete="CASCADE"))
)


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    building_id = Column(Integer, ForeignKey("buildings.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(Integer, default=lambda: int(time.time()))
    updated_at = Column(Integer, default=lambda: int(time.time()), onupdate=lambda: int(time.time()))

    building = relationship("Building", back_populates="organizations")
    activities = relationship(
        "Activity",
        secondary=organization_activity,
        back_populates="organizations",
        lazy="selectin"
    )
    phones = relationship("Phone", back_populates="organization", cascade="all, delete-orphan")


class Phone(Base):
    __tablename__ = "phones"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(50), nullable=False)
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )

    organization = relationship("Organization", back_populates="phones")


class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(500), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint('latitude >= -90 AND latitude <= 90', name='check_latitude'),
        CheckConstraint('longitude >= -180 AND longitude <= 180', name='check_longitude'),
    )

    organizations = relationship("Organization", back_populates="building", cascade="all, delete-orphan")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=True)
    level = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        CheckConstraint('level >= 0 AND level < 4', name='check_activity_level'),
    )

    parent = relationship("Activity", remote_side=[id], back_populates="children")
    children = relationship("Activity", back_populates="parent", cascade="all, delete-orphan")
    organizations = relationship(
        "Organization",
        secondary=organization_activity,
        back_populates="activities"
    )
