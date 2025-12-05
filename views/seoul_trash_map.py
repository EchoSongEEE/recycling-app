from __future__ import annotations

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from folium.plugins import MarkerCluster

from backend.trash_can_info import (
    annotate_distance,
    filter_by_gu,
    find_nearby,
    get_trash_cans,
    search_by_keyword,
)

st.set_page_config(
    page_title="쓰담 | 서울시 휴지통 지도",
    page_icon="🌿",
    layout="wide",
)

DEFAULT_CENTER = (37.5665, 126.9780)
DEFAULT_ZOOM = 12

st.markdown(
    """
    <style>
    header, .css-1l5rcnw {
        display: none !important; 
    }
    .stApp, .stApp > header {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    div[data-testid="stVerticalBlock"] > div:nth-child(1) {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    div[data-testid="stTitle"] {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    div[data-testid="stAppViewBlock"] {
        overflow: hidden !important; 
        height: 100vh;
    }

    section.main {
        overflow: hidden !important;
    }
    section.main > div {
        height: 100vh;
        overflow: hidden !important;
    }
    section.main > div > div {
        height: 100%;
    }

    div[data-testid="column"]:nth-of-type(1) > div {
        height: calc(100vh - 140px);
        max-height: calc(100vh - 140px);
        overflow-y: auto !important; 
        padding-right: 0.5rem;
    }

    div[data-testid="column"]:nth-of-type(2) {
        height: 100vh; 
    }
    div[data-testid="column"]:nth-of-type(2) > div {
        position: sticky;
        top: 0px; 
        align-self: flex-start;
        height: 100%;
    }
    
    .row1-wrap > div[data-testid="column"] > div {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def create_map(
    df: pd.DataFrame,
    center: tuple[float, float],
    zoom: int = 13,
    user_location: tuple[float, float] | None = None,
    radius_m: int | None = None,
    selected_bin_id: str | None = None,
) -> folium.Map:
    m = folium.Map(
        location=center, 
        zoom_start=zoom,
        tiles='OpenStreetMap',
        prefer_canvas=True
    )

    if len(df) > 100:
        marker_cluster = MarkerCluster(
            options={
                'maxClusterRadius': 50,
                'disableClusteringAtZoom': 16,
                'spiderfyOnMaxZoom': True,
                'chunkedLoading': True
            }
        ).add_to(m)
        
        for _, row in df.iterrows():
            addr = row.get("road_address") or row.get("jibun_address") or ""
            popup_html = f"""
            <b>{row['name']}</b><br/>
            {addr}<br/>
            {row['gu']} · {row.get('type') or '일반 휴지통'}
            """

            is_selected = selected_bin_id is not None and row["id"] == selected_bin_id
            icon_color = "orange" if is_selected else "blue"

            folium.Marker(
                location=[row["lat"], row["lng"]],
                icon=folium.Icon(color=icon_color, icon="trash", prefix="fa"),
                popup=folium.Popup(popup_html, max_width=250, lazy=True),
            ).add_to(marker_cluster)
    else:
        for _, row in df.iterrows():
            addr = row.get("road_address") or row.get("jibun_address") or ""
            popup_html = f"""
            <b>{row['name']}</b><br/>
            {addr}<br/>
            {row['gu']} · {row.get('type') or '일반 휴지통'}
            """

            is_selected = selected_bin_id is not None and row["id"] == selected_bin_id
            icon_color = "orange" if is_selected else "blue"

            folium.Marker(
                location=[row["lat"], row["lng"]],
                icon=folium.Icon(color=icon_color, icon="trash", prefix="fa"),
                popup=folium.Popup(popup_html, max_width=250, lazy=True),
            ).add_to(m)

    if user_location is not None:
        folium.Marker(
            location=user_location,
            icon=folium.Icon(color="red", icon="user", prefix="fa"),
            popup="내 위치",
        ).add_to(m)

        if radius_m is not None:
            folium.Circle(
                location=user_location,
                radius=radius_m,
                color="#ff6666",
                fill=False,
            ).add_to(m)

    return m


if "map_center" not in st.session_state:
    st.session_state["map_center"] = DEFAULT_CENTER
if "map_zoom" not in st.session_state:
    st.session_state["map_zoom"] = DEFAULT_ZOOM
if "selected_bin_id" not in st.session_state:
    st.session_state["selected_bin_id"] = None
if "list_limit" not in st.session_state:
    st.session_state["list_limit"] = 20
if "last_selected_gu" not in st.session_state:
    st.session_state["last_selected_gu"] = "전체"

location = get_geolocation()

user_location: tuple[float, float] | None = None
if location:
    try:
        coords = location.get("coords") or {}
        lat = coords.get("latitude")
        lon = coords.get("longitude")
        if lat is not None and lon is not None:
            user_location = (float(lat), float(lon))
    except (TypeError, KeyError, ValueError):
        user_location = None

has_user_loc = user_location is not None

st.title("🗺️ 서울시 휴지통 지도")
st.caption(
    "서울특별시 마포구 · 구로구 · 노원구 · 서초구 · 성북구 · 중랑구 공공 휴지통 위치 서비스를 제공해요."
)

@st.cache_data
def load_data() -> pd.DataFrame:
    return get_trash_cans()

GU_CENTERS = {
    "마포구": (37.5663, 126.9019),
    "구로구": (37.4954, 126.8874),
    "노원구": (37.6542, 127.0568),
    "서초구": (37.4837, 127.0324),
    "성북구": (37.5894, 127.0167),
    "중랑구": (37.6063, 127.0925),
}

df = load_data()

with st.sidebar:
    st.header("검색 / 필터")

    gu_options = ["전체", "마포구", "구로구", "노원구", "서초구", "성북구", "중랑구"]
    selected_gu = st.selectbox("자치구 선택", gu_options, index=0)

    if selected_gu != "전체" and selected_gu in GU_CENTERS:
        if st.session_state.get("last_selected_gu") != selected_gu:
            st.session_state["map_center"] = GU_CENTERS[selected_gu]
            st.session_state["map_zoom"] = 14
            st.session_state["selected_bin_id"] = None
            st.session_state["last_selected_gu"] = selected_gu
    elif selected_gu == "전체":
        if st.session_state.get("last_selected_gu") != "전체":
            st.session_state["map_center"] = DEFAULT_CENTER
            st.session_state["map_zoom"] = DEFAULT_ZOOM
            st.session_state["selected_bin_id"] = None
            st.session_state["last_selected_gu"] = "전체"

    search_text = st.text_input(
        "장소명 또는 도로명/지번 주소 검색",
        placeholder="예: 독막로 241, 서초역...",
    )

left, right = st.columns([0.4, 0.6])

nearby_mode: bool = False
radius_m: int = 300

with right:
    st.subheader("지도")

    st.markdown('<div class="row1-wrap">', unsafe_allow_html=True)
    row1_col1, row1_col2, row1_col3 = st.columns([0.12, 0.58, 0.30])

    with row1_col1:
        st.markdown("**📍 내 위치**")

    with row1_col2:
        if has_user_loc:
            lat, lon = user_location
            st.markdown(
                f"<span style='background:#cfe4ff;padding:4px 8px;border-radius:4px;'>"
                f"{lat:.5f}, {lon:.5f}</span>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("🔔 브라우저에서 위치 권한을 **허용**해 주세요.")

    with row1_col3:
        if st.button("위치 새로고침", use_container_width=True):
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

filtered = filter_by_gu(df, selected_gu if selected_gu != "전체" else None)
filtered = search_by_keyword(filtered, search_text)

if nearby_mode and has_user_loc:
    filtered = find_nearby(
        filtered,
        user_location[0],
        user_location[1],
        radius_m=radius_m,
        limit=None,
    )
elif has_user_loc:
    filtered = annotate_distance(filtered, user_location[0], user_location[1])
else:
    filtered = filtered.copy()
    filtered["distance_m"] = None

with left:
    st.subheader("🗑️ 휴지통 목록")

    st.caption(
        f"조건에 해당하는 휴지통: **{len(filtered)}개**"
        + (
            " (내 위치 기준 거리순)"
            if nearby_mode and has_user_loc
            else " (자치구/검색 기준)"
        )
    )

    if filtered.empty:
        st.warning("조건에 맞는 휴지통이 없어요 🥲", icon="⚠️")
    else:
        if "distance_m" in filtered.columns and filtered["distance_m"].notnull().any():
            filtered_disp = filtered.sort_values("distance_m")
        else:
            filtered_disp = filtered.sort_values(["gu", "name"])

        limit = st.session_state["list_limit"]
        subset = filtered_disp.head(limit)

        for _, row in subset.iterrows():
            dist_m = row.get("distance_m", None)
            dist_text = (
                f"{dist_m:.0f} m" if dist_m is not None and not pd.isna(dist_m) else "- m"
            )

            with st.container(border=True):
                st.markdown(f"**{row['name']}**")
                addr = row.get("road_address") or row.get("jibun_address") or ""
                if addr:
                    st.caption(addr)

                detail_line = f"{row['gu']} · {row.get('type') or '일반 휴지통'}"
                if isinstance(row.get("detail"), str) and row["detail"].strip():
                    detail_line += f" · {row['detail']}"
                st.write(detail_line)

                footer_left, footer_right = st.columns([0.5, 0.5])
                with footer_left:
                    if has_user_loc:
                        st.text(f"📍 내 위치로부터 {dist_text}")
                with footer_right:
                    if st.button("지도에서 보기", key=f"focus-{row['id']}", use_container_width=True):
                        st.session_state["selected_bin_id"] = row["id"]
                        st.session_state["map_center"] = (row["lat"], row["lng"])
                        st.session_state["map_zoom"] = 18

        if len(filtered_disp) > limit:
            if st.button("더 보기", key="load_more"):
                st.session_state["list_limit"] += 20
        else:
            st.caption("모든 휴지통 정보를 다 불러왔어요 🙂")

with right:
    if filtered.empty:
        st.info("지도로 표시할 데이터가 없어요.", icon="ℹ️")
    else:
        center = st.session_state.get("map_center", DEFAULT_CENTER)
        zoom = st.session_state.get("map_zoom", DEFAULT_ZOOM)

        if has_user_loc and st.session_state.get("selected_bin_id") is None:
            center = user_location
            zoom = 15 if nearby_mode else 13

        folium_map = create_map(
            df=filtered,
            center=center,
            zoom=zoom,
            user_location=user_location,
            radius_m=radius_m if (nearby_mode and has_user_loc) else None,
            selected_bin_id=st.session_state.get("selected_bin_id"),
        )

        st_folium(
            folium_map,
            width="100%",
            height=600,
            returned_objects=[]
        )