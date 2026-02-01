from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional, Tuple
import math
from app import models, schemas
from app.config import settings


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Расчет расстояния между двумя точками (в метрах)
    Использует формулу гаверсинусов
    """
    R = 6371000  # Радиус Земли в метрах

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def get_organization(db: Session, organization_id: int) -> Optional[models.Organization]:
    return db.query(models.Organization).filter(models.Organization.id == organization_id).first()


def get_organizations(db: Session, skip: int = 0, limit: int = 100) -> List[models.Organization]:
    return db.query(models.Organization).offset(skip).limit(limit).all()


def create_organization(db: Session, organization: schemas.OrganizationCreate) -> models.Organization:
    db_organization = models.Organization(
        name=organization.name,
        description=organization.description,
        building_id=organization.building_id
    )

    # Добавляем телефоны
    if organization.phone_numbers:
        for phone_number in organization.phone_numbers:
            db_phone = models.Phone(number=phone_number)
            db_organization.phones.append(db_phone)

    # Добавляем виды деятельности
    if organization.activity_ids:
        activities = db.query(models.Activity).filter(
            models.Activity.id.in_(organization.activity_ids)
        ).all()
        db_organization.activities.extend(activities)

    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization


def update_organization(
        db: Session,
        organization_id: int,
        organization: schemas.OrganizationUpdate
) -> Optional[models.Organization]:
    db_organization = get_organization(db, organization_id)
    if not db_organization:
        return None

    # Обновляем основные поля
    update_data = organization.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field not in ['phone_numbers', 'activity_ids']:
            setattr(db_organization, field, value)

    # Обновляем телефоны
    if organization.phone_numbers is not None:
        # Удаляем старые телефоны
        db.query(models.Phone).filter(
            models.Phone.organization_id == organization_id
        ).delete()

        # Добавляем новые
        for phone_number in organization.phone_numbers:
            db_phone = models.Phone(number=phone_number, organization_id=organization_id)
            db.add(db_phone)

    # Обновляем виды деятельности
    if organization.activity_ids is not None:
        # Очищаем текущие связи
        db_organization.activities.clear()

        # Добавляем новые
        activities = db.query(models.Activity).filter(
            models.Activity.id.in_(organization.activity_ids)
        ).all()
        db_organization.activities.extend(activities)

    db.commit()
    db.refresh(db_organization)
    return db_organization


def delete_organization(db: Session, organization_id: int) -> bool:
    db_organization = get_organization(db, organization_id)
    if not db_organization:
        return False

    db.delete(db_organization)
    db.commit()
    return True


def get_organizations_by_building(db: Session, building_id: int) -> List[models.Organization]:
    return db.query(models.Organization).filter(
        models.Organization.building_id == building_id
    ).all()


def get_organizations_by_activity(db: Session, activity_id: int) -> List[models.Organization]:
    activity_ids = get_all_child_activity_ids(db, activity_id)

    return db.query(models.Organization).join(models.Organization.activities).filter(
        models.Activity.id.in_(activity_ids)
    ).distinct().all()


def search_organizations_by_name(db: Session, name: str) -> List[models.Organization]:
    return db.query(models.Organization).filter(
        models.Organization.name.ilike(f"%{name}%")
    ).all()


def search_organizations_by_activity_name(db: Session, activity_name: str) -> List[models.Organization]:
    # Находим активности по имени
    activities = db.query(models.Activity).filter(
        models.Activity.name.ilike(f"%{activity_name}%")
    ).all()

    if not activities:
        return []

    # Получаем все ID активностей (включая дочерние)
    activity_ids = []
    for activity in activities:
        activity_ids.extend(get_all_child_activity_ids(db, activity.id))

    # Получаем организации
    return db.query(models.Organization).join(models.Organization.activities).filter(
        models.Activity.id.in_(activity_ids)
    ).distinct().all()


def get_organizations_in_radius(
        db: Session,
        lat: float,
        lon: float,
        radius: float = None
) -> List[models.Organization]:
    if radius is None:
        radius = settings.DEFAULT_SEARCH_RADIUS

    buildings = db.query(models.Building).all()

    # Фильтруем здания по расстоянию
    nearby_building_ids = []
    for building in buildings:
        distance = haversine_distance(lat, lon, building.latitude, building.longitude)
        if distance <= radius:
            nearby_building_ids.append(building.id)

    return db.query(models.Organization).filter(
        models.Organization.building_id.in_(nearby_building_ids)
    ).all()


def get_organizations_in_rectangle(
        db: Session,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float
) -> List[models.Organization]:
    # Находим здания в прямоугольной области
    buildings = db.query(models.Building).filter(
        and_(
            models.Building.latitude >= min_lat,
            models.Building.latitude <= max_lat,
            models.Building.longitude >= min_lon,
            models.Building.longitude <= max_lon
        )
    ).all()

    building_ids = [building.id for building in buildings]

    # Получаем организации в этих зданиях
    return db.query(models.Organization).filter(
        models.Organization.building_id.in_(building_ids)
    ).all()


def get_building(db: Session, building_id: int) -> Optional[models.Building]:
    return db.query(models.Building).filter(models.Building.id == building_id).first()


def get_buildings(db: Session, skip: int = 0, limit: int = 100) -> List[models.Building]:
    return db.query(models.Building).offset(skip).limit(limit).all()


def create_building(db: Session, building: schemas.BuildingCreate) -> models.Building:
    db_building = models.Building(**building.model_dump())
    db.add(db_building)
    db.commit()
    db.refresh(db_building)
    return db_building


def update_building(
        db: Session,
        building_id: int,
        building: schemas.BuildingUpdate
) -> Optional[models.Building]:
    db_building = get_building(db, building_id)
    if not db_building:
        return None

    for field, value in building.model_dump(exclude_unset=True).items():
        setattr(db_building, field, value)

    db.commit()
    db.refresh(db_building)
    return db_building


def delete_building(db: Session, building_id: int) -> bool:
    db_building = get_building(db, building_id)
    if not db_building:
        return False

    db.delete(db_building)
    db.commit()
    return True


def get_activity(db: Session, activity_id: int) -> Optional[models.Activity]:
    return db.query(models.Activity).filter(models.Activity.id == activity_id).first()


def get_activities(db: Session, skip: int = 0, limit: int = 100) -> List[models.Activity]:
    return db.query(models.Activity).filter(models.Activity.parent_id.is_(None)).offset(skip).limit(limit).all()


def get_all_child_activity_ids(db: Session, parent_id: int) -> List[int]:
    """
    Рекурсивно получает все ID дочерних активностей
    """
    result = [parent_id]

    children = db.query(models.Activity).filter(models.Activity.parent_id == parent_id).all()
    for child in children:
        result.extend(get_all_child_activity_ids(db, child.id))

    return result


def create_activity(db: Session, activity: schemas.ActivityCreate) -> models.Activity:
    # Проверяем уровень вложенности
    if activity.parent_id:
        parent = get_activity(db, activity.parent_id)
        if not parent:
            raise ValueError(f"Parent activity {activity.parent_id} not found")

        if parent.level >= settings.MAX_ACTIVITY_LEVEL - 1:
            raise ValueError(
                f"Cannot create activity at level {parent.level + 1}. Max level is {settings.MAX_ACTIVITY_LEVEL}")

        level = parent.level + 1
    else:
        level = 0

    db_activity = models.Activity(
        name=activity.name,
        description=activity.description,
        parent_id=activity.parent_id,
        level=level
    )

    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity


def update_activity(
        db: Session,
        activity_id: int,
        activity: schemas.ActivityUpdate
) -> Optional[models.Activity]:
    db_activity = get_activity(db, activity_id)
    if not db_activity:
        return None

    # Если меняется parent_id, нужно проверить уровень вложенности
    if activity.parent_id is not None and activity.parent_id != db_activity.parent_id:
        if activity.parent_id == activity_id:
            raise ValueError("Activity cannot be its own parent")

        parent = get_activity(db, activity.parent_id)
        if not parent:
            raise ValueError(f"Parent activity {activity.parent_id} not found")

        if parent.level >= settings.MAX_ACTIVITY_LEVEL - 1:
            raise ValueError(
                f"Cannot move activity to level {parent.level + 1}. Max level is {settings.MAX_ACTIVITY_LEVEL}")

        # Обновляем уровень и всех потомков
        update_activity_level(db, activity_id, parent.level + 1)

    for field, value in activity.model_dump(exclude_unset=True).items():
        if field != 'parent_id':
            setattr(db_activity, field, value)

    if activity.parent_id is not None:
        db_activity.parent_id = activity.parent_id

    db.commit()
    db.refresh(db_activity)
    return db_activity


def update_activity_level(db: Session, activity_id: int, new_level: int):
    """
    Рекурсивно обновляет уровень активности и всех её потомков
    """
    if new_level >= settings.MAX_ACTIVITY_LEVEL:
        raise ValueError(f"Cannot set level {new_level}. Max level is {settings.MAX_ACTIVITY_LEVEL}")

    db_activity = get_activity(db, activity_id)
    if db_activity:
        db_activity.level = new_level

        # Обновляем всех детей
        children = db.query(models.Activity).filter(models.Activity.parent_id == activity_id).all()
        for child in children:
            update_activity_level(db, child.id, new_level + 1)


def delete_activity(db: Session, activity_id: int) -> bool:
    db_activity = get_activity(db, activity_id)
    if not db_activity:
        return False

    db.delete(db_activity)
    db.commit()
    return True


def get_activity_tree(db: Session, parent_id: Optional[int] = None) -> List[models.Activity]:
    if parent_id:
        activities = db.query(models.Activity).filter(models.Activity.parent_id == parent_id).all()
    else:
        activities = db.query(models.Activity).filter(models.Activity.parent_id.is_(None)).all()

    for activity in activities:
        activity.children = get_activity_tree(db, activity.id)

    return activities
