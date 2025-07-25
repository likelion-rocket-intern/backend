import requests, json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import re
from app.utils.crawler.module.jumpit_crawler import jumpit_extract
from app.utils.crawler.module.wanted_crawler import wanted_extract


# 뽑아오는 방식은 달라도, 가져오는건 같음
class JobCrawler:
    #헤더 
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_site_name(self, url):
        """URL에서 사이트명 추출"""
        domain = urlparse(url).netloc.lower()
        
        if 'jumpit' in domain:
            return 'jumpit'
        elif 'wanted' in domain:
            return 'wanted'
        else:
            return None
    
    def fetch_html(self, url):
        """HTML 가져오기"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"HTML 가져오기 실패: {e}")
            return None
    
    def crawl(self, url):
        """메인 크롤링 함수"""
        print(f"크롤링 시작: {url}")
        
        # 사이트 구분
        site_name = self.get_site_name(url)
        if not site_name:
            return {
                'status': 'error',
                'message': f'지원하지 않는 사이트입니다. 현재 지원하는 사이트: Jumpit, Saramin, JobKorea, Wanted, Programmers, GreetingHR',
                'url': url
            }
        
        print(f"사이트: {site_name}")
        
        # HTML 가져오기
        html = self.fetch_html(url)
        if not html:
            return {
                'status': 'error',
                'message': '해당 URL에서 데이터를 불러올 수 없습니다.',
                'url': url
            }
        
        # 사이트별 크롤링 모듈 호출
        result = self.crawl_by_site(site_name, html, url)
        return result
    
    def crawl_by_site(self, site_name, html, url):
        """사이트별 크롤링 모듈 호출"""
        print(f"{site_name} 전용 크롤링 실행")
        
        if site_name == 'jumpit':
            return jumpit_extract(html, url)
        elif site_name == 'wanted':
            return wanted_extract(html, url)
        else:
            return {
                'site': site_name,
                'url': url,
                'status': 'error',
                'message': f'{site_name} 크롤러가 아직 구현되지 않은 플랫 폼이거나 크롤링에 실패했습니다.'
            }

def get_wanted_jobs(limit : int = 10):
    # API URL
    wanted_url = "https://www.wanted.co.kr/api/v4/jobs"

    # 요청 파라미터
    params = {
        "country": "kr",
        "job_sort": "job.popularity_order",
        "locations": "all",
        "years": -1,
        "limit": limit,  # 한 페이지당 가져올 항목 수
        "offset": 0   # 시작 위치
    }

    # HTTP 요청 헤더
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json"
    }

    # 결과를 저장할 리스트
    jobs_data = []

    # API 요청
    response = requests.get(wanted_url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        
        # 데이터 추출
        if 'data' in data:
            for job in data['data']:
                jobs_data.append(f"https://www.wanted.co.kr/wd/{job.get('id')}")
    else:
        print(f"Error: {response.status_code}")

    return jobs_data

# =========================
# 사용 함수
# =========================
def crawl_url(url):
    """URL을 입력받아서 크롤링"""

    crawler = JobCrawler()
    result = crawler.crawl(url)
    return result

# 채신 정보들을 50개 정도 크롤링
def crawl_periodically(url):
    """일단 웹에서 크롤링할 사이트를 찾아봄"""
    crawler = JobCrawler()
    results = []

    # 1. 목록 페이지에서 상세 공고 링크 추출 함수
    wanted_links = get_wanted_jobs(50)
   
    # 2. 공고 페이지 크롤링
    for url in wanted_links:
        result = crawler.crawl(url)
        results.append(result)

    return results