import streamlit as st

from views.coach import page as coach_page
from views.seoul_trash_map import page as trash_page
from views.seoul_waste_request import page as waste_page
from views.zerowaste_map import page as zerowaste_page
from views.dropoff_map import page as dropoff_page

st.set_page_config(
    page_title="쓰담 | 재활용 분리배출 코치",
    page_icon="🌿",
    layout="wide",
)

pages = [
    st.Page(
        coach_page,
        title="재활용 분리배출 코칭",
        icon="🌿",
        url_path="coach",       
    ),
    st.Page(
        trash_page,
        title="서울시 휴지통 지도",
        icon="🗑️",
        url_path="trash-cans",     
    ),
    st.Page(
        waste_page,
        title="서울시 폐기물 신청 지도",
        icon="🚚",
        url_path="waste-request", 
    ),
    st.Page(
        zerowaste_page,
        title="제로웨이스트 샵 찾기",
        icon="🌱",
        url_path="zerowaste-shops",  
    ),
    st.Page(
        dropoff_page,
        title="분리배출 장소 지도",
        icon="📦",
        url_path="dropoff-spots",   
    ),
]

nav = st.navigation(pages)
nav.run()
