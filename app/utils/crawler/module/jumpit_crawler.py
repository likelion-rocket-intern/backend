from bs4 import BeautifulSoup
import re

def jumpit_extract(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')

    # HTML에서 raw 텍스트 추출
    for tag in soup(["script", "style", "noscript", "nav", "footer", "aside"]):
        tag.decompose()
    
    div = soup.find("div", class_="position_info") or soup.find('body')
    div2 = soup.find("div", class_="sc-b12ae455-0 ehVsnD") or soup.find('body')
    if div:
        text = div.get_text()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()

        if div2 :
            text2 = div2.get_text(separator='\n')  # 각 블록마다 줄바꿈
            text2 = re.sub(r'\n+', '\n', text2)    # 연속 줄바꿈 하나로
            text2 = re.sub(r'[ \t]+', ' ', text2)  # 여러 공백 하나로
            text2 = text2.strip()
            

        return {
            'site': 'jumpit',
            'url': url,
            'status': 'success',
            'raw_data': text + text2
        }
    return {
        'site': 'jumpit',
        'url': url,
        'status': 'error',
        'message': '콘텐츠를 찾을 수 없습니다.'
    }