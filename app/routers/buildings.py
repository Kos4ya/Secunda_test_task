from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session
from app import crud, schemas, dependencies
from app.database import get_db

router = APIRouter()


@router.get("/buildings", response_model=List[schemas.Building])
def read_buildings(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: Session = Depends(get_db),
        api_key: str = Depends(dependencies.get_api_key)
):
    """
    Получить список всех зданий с пагинацией
    """
    buildings = crud.get_buildings(db, skip=skip, limit=limit)
    return buildings


@router.get("/buildings/{building_id}", response_model=schemas.Building)
def read_building(
        building_id: int,
        db: Session = Depends(get_db),
        api_key: str = Depends(dependencies.get_api_key)
):
    """
    Получить информацию о здании по его ID
    """
    building = crud.get_building(db, building_id=building_id)
    if building is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found"
        )
    return building


@router.post("/buildings", response_model=schemas.Building, status_code=status.HTTP_201_CREATED)
def create_building(
        building: schemas.BuildingCreate,
        db: Session = Depends(get_db),
        api_key: str = Depends(dependencies.get_api_key)
):
    """
    Создать новое здание
    """
    return crud.create_building(db=db, building=building)


@router.put("/buildings/{building_id}", response_model=schemas.Building)
def update_building(
        building_id: int,
        building: schemas.BuildingUpdate,
        db: Session = Depends(get_db),
        api_key: str = Depends(dependencies.get_api_key)
):
    """
    Обновить информацию о здании
    """
    db_building = crud.update_building(db, building_id=building_id, building=building)
    if db_building is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found"
        )
    return db_building


@router.delete("/buildings/{building_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_building(
        building_id: int,
        db: Session = Depends(get_db),
        api_key: str = Depends(dependencies.get_api_key)
):
    """
    Удалить здание
    """
    success = crud.delete_building(db, building_id=building_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found"
        )
