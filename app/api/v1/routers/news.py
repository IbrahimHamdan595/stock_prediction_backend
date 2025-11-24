from fastapi import APIRouter, Depends

from app.api.v1.dependencies.auth import get_current_active_user
from app.db.mongo import get_db
from app.schemas.market import NewsIn, NewsOut
from app.services.news_service import NewsService

router = APIRouter()


@router.post("/", response_model=NewsOut)
async def create_news(payload: NewsIn, db=Depends(get_db), user=Depends(get_current_active_user)):
    service = NewsService(db)
    return await service.add_news(payload)


@router.get("/{symbol}", response_model=list[NewsOut])
async def get_news(symbol: str, sentiment_label: str | None = None, db=Depends(get_db), user=Depends(get_current_active_user)):
    service = NewsService(db)
    return await service.get_news(symbol, sentiment_label)
