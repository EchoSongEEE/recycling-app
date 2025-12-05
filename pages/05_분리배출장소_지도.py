import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="쓰담 | 서울시 분리배출 장소 지도", page_icon="🌿")

st.subheader("🗺️ 서울시 분리배출 장소 지도")

# 지도 중심 좌표 설정 (사용자의 현위치 / 기본좌표 - 서울시청)
location = get_geolocation()

center_lat = 37.5665 # 기본 좌표
center_lon = 126.9780
zoom_level = 15

if location :
    try:
        center_lat = location['coords']['latitude']
        center_lon = location['coords']['longitude']
    except (TypeError, KeyError):
        pass


m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level)

# 현재 내 위치 마커 찍기 (빨간색 아이콘)
folium.Marker(
    [center_lat, center_lon],
    popup="내 위치",
    tooltip="현재 계신 곳입니다",
    icon=folium.Icon(color='red', icon='user')
).add_to(m)

# 분리배출 장소 마커
recycling_spots = [
    {"name": "재활용품 수거함", "lat": 37.531405951, "lon": 126.968820855, "loc": "서울특별시 용산구 한강대로39길 34-5"},
    {"name": "재활용품 수거함", "lat": 37.526158356, "lon": 126.963991217, "loc": "서울특별시 용산구 한강대로15길 8-5"},
    {"name": "재활용품 수거함", "lat": 37.532477219, "lon": 126.992280033, "loc": "서울특별시 용산구 녹사평대로26가길 13"},
    {"name": "재활용품 수거함", "lat": 37.546230421, "lon": 126.968248405, "loc": "서울특별시 용산구 청파로57가길 20"},
    {"name": "재활용품 수거함", "lat": 37.543276420, "lon": 126.967577129, "loc": "서울특별시 용산구 청파로43길 47-16"},
    {"name": "재활용품 수거함", "lat": 37.542685125, "lon": 126.964364030, "loc": "서울특별시 용산구 백범로79길 91"},
    {"name": "재활용품 수거함", "lat": 37.553795554, "lon": 126.977122664, "loc": "서울특별시 용산구 소월로2나길 15-7"},
    {"name": "재활용품 수거함", "lat": 37.542541740, "lon": 126.963011087, "loc": "서울특별시 용산구 효창원로72길 23"},
    {"name": "재활용품 수거함", "lat": 37.534944062, "lon": 126.990599864, "loc": "서울특별시 용산구 이태원로15길 18"},
]

for spot in recycling_spots:
    folium.Marker(
        [spot["lat"], spot["lon"]], 
        popup=spot["name"],
        tooltip=spot["loc"]
    ).add_to(m)

# 지도 출력
st_folium(m, width="100%", height=500)