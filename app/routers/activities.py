from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.orm import Session
from app import crud, schemas, dependencies
from app.database import get_db

router = APIRouter()


@router.get("/activities", response_model=List[schemas.Activity])
def read_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.get_api_key)
):
    """
    Получить список всех видов деятельности (только корневые) с пагинацией
    """
    activities = crud.get_activities(db, skip=skip, limit=limit)
    return activities


@router.get("/activities/tree", response_model=List[schemas.Activity])
def read_activity_tree(
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.get_api_key)
):
    """
    Получить полное дерево видов деятельности
    """
    activities = crud.get_activity_tree(db)
    return activities


@router.get("/activities/{activity_id}", response_model=schemas.Activity)
def read_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.get_api_key)
):
    """
    Получить информацию о виде деятельности по его ID
    """
    activity = crud.get_activity(db, activity_id=activity_id)
    if activity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    return activity


@router.post("/activities", response_model=schemas.Activity, status_code=status.HTTP_201_CREATED)
def create_activity(
    activity: schemas.ActivityCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.get_api_key)
):
    """
    Создать новый вид деятельности
    """
    try:
        return crud.create_activity(db=db, activity=activity)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/activities/{activity_id}", response_model=schemas.Activity)
def update_activity(
    activity_id: int,
    activity: schemas.ActivityUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.get_api_key)
):
    """
    Обновить информацию о виде деятельности
    """
    try:
        db_activity = crud.update_activity(db, activity_id=activity_id, activity=activity)
        if db_activity is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found"
            )
        return db_activity
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(dependencies.get_api_key)
):
    """
    Удалить вид деятельности (удаляет также все дочерние виды)
    """
    success = crud.delete_activity(db, activity_id=activity_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )