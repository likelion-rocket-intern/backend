from fastapi import APIRouter

from app.service.crawler_service import CrawlerService



# 일단은 테스트용 크롤러 라우터임
crawler_service = CrawlerService()

router = APIRouter(tags=["crawler"])

@router.get("/")
async def get_crawler():
    return crawler_service.crawl_test()