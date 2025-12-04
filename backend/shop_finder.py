import requests
import pandas as pd
import re
import streamlit as st

try:
    CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
    CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
except Exception:
    CLIENT_ID = ""
    CLIENT_SECRET = ""

def clean_html(text):
    """API 결과에 섞인 <b> 태그 등을 제거하는 함수"""
    if not isinstance(text, str):
        return text
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', text)
    return cleantext

def get_shops_by_location(location):
    """
    지역명을 받아 제로웨이스트 샵 정보를 반환합니다.
    """
    if not location:
        return pd.DataFrame()
    
    query = f"{location} 제로웨이스트"
    url = "https://openapi.naver.com/v1/search/local.json"
    
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }
    
    params = {
        "query": query,
        "display": 10,  
        "sort": "random" 
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            st.error(f"🚨 API 호출 에러 발생! (코드: {response.status_code})")
            st.error(f"메시지: {response.text}")
            return pd.DataFrame()

        data = response.json()
        items = data.get('items', [])
        
        if not items:
            return pd.DataFrame()

        shop_list = []
        for item in items:
            shop_list.append({
                'title': clean_html(item['title']),
                'category': clean_html(item['category']),
                'address': item['roadAddress'] if item['roadAddress'] else item['address'],
                'link': item['link']
            })
        
        return pd.DataFrame(shop_list)
            
    except Exception as e:
        st.error(f"시스템 에러 발생: {e}")
        return pd.DataFrame()