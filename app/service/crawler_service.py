
# 크롤러 테스팅

from app.utils.crawler.main_crawler import crawl_url


class CrawlerService:
    
    # 대충 크롤링 불러오는 메서드
    def crawl_test(self):
        return crawl_url("https://www.wanted.co.kr/wd/256242")