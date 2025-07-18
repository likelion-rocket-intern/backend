from bs4 import BeautifulSoup
import re

def saramin_extract(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')

    # "user_content" 클래스를 가진 div 찾기
    user_content_div = soup.find("div", class_="user_content")
    if user_content_div:
        text = user_content_div.get_text(separator='\n')
        text = text.strip()
        return {
            'site': 'saramin',
            'url': url,
            'status': 'success',
            'raw_data': text
        }
    else:
        return {
            'site': 'saramin',
            'url': url,
            'status': 'error',
            'message': 'user_content를 찾을 수 없습니다.'
        }