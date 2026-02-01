from fastapi import Header, HTTPException, status
from app.config import settings


async def get_api_key(x_api_key: str = Header(...)):
    """
    Проверка статического API ключа
    """
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    return x_api_key