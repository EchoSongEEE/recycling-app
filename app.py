import streamlit as st

from views.coach import page as coach_page
from views.seoul_trash_map import page as trash_page
from views.seoul_waste_request import page as waste_page
from views.zerowaste_map import page as zerowaste_page
from views.dropoff_map import page as dropoff_page

st.set_page_config(
    page_title="재활용 분리배출 코칭",
    page_icon="♻️",
    layout="wide",
)

nav = st.navigation(
    [
        st.Page(coach_page, title="재활용 분리배출 코칭"),
        st.Page(trash_page, title="서울시 휴지통 지도"),
        st.Page(waste_page, title="서울시 폐기물 신청 지도"),
        st.Page(zerowaste_page, title="제로웨이스트 지도"),
        st.Page(dropoff_page, title="분리배출장소 지도"),
    ]
)

nav.run()
