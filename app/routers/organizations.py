from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session

from app import crud, schemas, dependencies
from app.database import get_db

router = APIRouter()


@router.get("/organizations", response_model=List[schemas.Organization])
def get_organizations(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        api_key: str = Depends(dependencies.get_api_key)
):
    """Получить список организаций"""
    organizations = crud.get_organizations(db, skip=skip, limit=limit)
    return organizations


@router.get("/organizations/by-building/{building_id}", response_model=List[schemas.Organization])
def get_organizations_by_building(
        building_id: int,
        db: Session = Depends(get_db),
        api_key: str = Depends(dependencies.get_api_key)
):
    """Список организаций в конкретном здании"""
    organizations = crud.get_organizations_by_building(db, building_id=building_id)
    return organizations


@router.get("/organizations/by-activity/{activity_id}", response_model=List[schemas.Organization])
def get_organizations_by_activity(
        activity_id: int,
        db: Session = Depends(get_db),
        api_key: str = Depends(dependencies.get_api_key)
):
    """Список организаций по виду деятельности"""
    organizations = crud.get_organizations_by_activity(db, activity_id=activity_id)
    return organizations


@router.get("/organizations/nearby", response_model=List[schemas.Organization])
def get_organizations_nearby(
        lat: float = Query(..., description="Широта центра"),
        lon: float = Query(..., description="Долгота центра"),
        radius: float = Query(1000, description="Радиус в метрах"),
        db: Session = Depends(get_db),
        api_key: str = Depends(dependencies.get_api_key)
):
    """Организации в заданном радиусе от точки"""
    organizations = crud.get_organizations_in_radius(db, lat=lat, lon=lon, radius=radius)
    return organizations


@router.get("/organizations/search", response_model=List[schemas.Organization])
def search_organizations(
        name: Optional[str] = None,
        activity_name: Optional[str] = None,
        db: Session = Depends(get_db),
        api_key: str = Depends(dependencies.get_api_key)
):
    """Поиск организаций по названию или виду деятельности"""
    if name:
        return crud.search_organizations_by_name(db, name=name)
    elif activity_name:
        return crud.search_organizations_by_activity_name(db, activity_name=activity_name)
    else:
        raise HTTPException(status_code=400, detail="Укажите параметр поиска")


@router.post("/organizations", response_model=schemas.Organization, status_code=status.HTTP_201_CREATED)
def create_organization(
        organization: schemas.OrganizationCreate,
        db: Session = Depends(get_db),
        api_key: str = Depends(dependencies.get_api_key)
):
    """
    Создать новую организацию
    """
    return crud.create_organization(db=db, organization=organization)


@router.put("/organizations/{organization_id}", response_model=schemas.Organization)
def update_organization(
        organization_id: int,
        organization: schemas.OrganizationUpdate,
        db: Session = Depends(get_db),
        api_key: str = Depends(dependencies.get_api_key)
):
    """
    Обновить информацию об организации
    """
    db_organization = crud.update_organization(db, organization_id=organization_id, organization=organization)
    if db_organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    return db_organization


@router.delete("/organizations/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(
        organization_id: int,
        db: Session = Depends(get_db),
        api_key: str = Depends(dependencies.get_api_key)
):
    """
    Удалить организацию
    """
    success = crud.delete_organization(db, organization_id=organization_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
