
# 크롤러 테스팅

from app.utils.crawler.main_crawler import crawl_url


class CrawlerService:
    
    # 대충 크롤링 불러오는 메서드
    def crawl_test(self):
        return crawl_url("https://www.saramin.co.kr/zf_user/jobs/relay/view?isMypage=no&rec_idx=51241350&recommend_ids=eJxVj8kRA0EIA6PxX%2BLm7UA2%2Fyw8a9cO42eXoBFOuEr7VeQr305lqtjVkC8yIzR3KhGeeBBtDNRC%2FNJut9zIRhkfFdyEYVvFWqq5K2JLftylds9wWEXNcCsxrRCw44XVKaiTataBK238fVScVmLL1ge22r2LDxOgP7Q%3D&view_type=list&gz=1&t_ref_content=general&t_ref=area_recruit&relayNonce=3cb306c0dbf778d73d7e&immediately_apply_layer_open=n#seq=0")