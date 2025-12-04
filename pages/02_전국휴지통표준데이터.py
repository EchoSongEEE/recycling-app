from __future__ import annotations

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation

from backend.trash_can_info import (
    annotate_distance,
    filter_by_gu,
    find_nearby,
    get_trash_cans,
    search_by_keyword,
)

st.set_page_config(
    page_title="서울 휴지통 지도",
    page_icon="🗑️",
    layout="wide",
)

DEFAULT_CENTER = (37.5665, 126.9780)  # 서울 시청
DEFAULT_ZOOM = 12

st.markdown(
    """
    <style>
    /* 첫 번째 컬럼(왼쪽): 세로 스크롤 가능 영역로 제한 */
    div[data-testid="column"]:nth-of-type(1) > div {
        max-height: calc(100vh - 140px);
        overflow-y: auto;
        padding-right: 0.5rem;
    }

    /* 두 번째 컬럼(오른쪽): 화면 상단에 sticky 고정 */
    div[data-testid="column"]:nth-of-type(2) > div {
        position: sticky;
        top: 80px;
        align-self: flex-start;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> pd.DataFrame:
    return get_trash_cans()


def create_map(
    df: pd.DataFrame,
    center: tuple[float, float],
    zoom: int = 13,
    user_location: tuple[float, float] | None = None,
    radius_m: int | None = None,
    selected_bin_id: str | None = None,
) -> folium.Map:
    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")

    # 휴지통 마커
    for _, row in df.iterrows():
        addr = row.get("road_address") or row.get("jibun_address") or ""
        popup_html = f"""
        <b>{row['name']}</b><br/>
        {addr}<br/>
        {row['gu']} · {row.get('type') or '일반 휴지통'}
        """

        is_selected = selected_bin_id is not None and row["id"] == selected_bin_id
        icon_color = "blue"
        if is_selected:
            icon_color = "orange"  # 선택된 휴지통은 주황색으로 강조

        folium.Marker(
            location=[row["lat"], row["lng"]],
            icon=folium.Icon(color=icon_color, icon="trash", prefix="fa"),
            popup=folium.Popup(popup_html, max_width=250),
        ).add_to(m)

    # 내 위치 마커 (빨간색)
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


def main():
    if "map_center" not in st.session_state:
        st.session_state["map_center"] = DEFAULT_CENTER
    if "map_zoom" not in st.session_state:
        st.session_state["map_zoom"] = DEFAULT_ZOOM
    if "selected_bin_id" not in st.session_state:
        st.session_state["selected_bin_id"] = None
    if "list_limit" not in st.session_state:
        st.session_state["list_limit"] = 20  # 리스트 처음에 20개만

    st.title("서울 휴지통 지도 🗺️")
    st.caption(
        "서울특별시 마포구 · 구로구 · 노원구 · 서초구 · 성북구 · 중랑구 공공 휴지통 위치 서비스"
    )

    df = load_data()

    with st.sidebar:
        st.header("검색 / 필터")

        gu_options = ["전체", "마포구", "구로구", "노원구", "서초구", "성북구", "중랑구"]
        selected_gu = st.selectbox("자치구 선택", gu_options, index=0)

        search_text = st.text_input(
            "장소명 또는 도로명/지번 주소 검색",
            placeholder="예: 독막로 241, 서초역...",
        )

    left, right = st.columns([0.4, 0.6])

    user_location: tuple[float, float] | None = None
    nearby_mode: bool = False
    radius_m: int = 300

    # 오른쪽 영역
    with right:
        st.subheader("지도")

        row1_col1, row1_col2 = st.columns([0.1, 0.9])

        with row1_col1:
            loc = streamlit_geolocation()

        with row1_col2:
            if isinstance(loc, dict) and loc.get("latitude") is not None:
                user_location = (float(loc["latitude"]), float(loc["longitude"]))
                # 출력 문구를 한 줄로 압축
                st.markdown(f"**내 위치:** {user_location[0]:.5f}, {user_location[1]:.5f}")
            else:
                st.markdown("**📍 내 위치 정보가 없어요.**")

        row2_col1, row2_col2 = st.columns([0.35, 0.65])
        with row2_col1:
            nearby_mode = st.checkbox("내 주변만", value=False)
        with row2_col2:
            radius_m = st.slider(
                "반경 (m)",
                min_value=100,
                max_value=1000,
                value=300,
                step=50,
            )

    has_user_loc = user_location is not None

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
        st.subheader("휴지통 목록")

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
            # 거리 정보가 있으면 거리순, 아니면 구/이름순
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

                    if has_user_loc:
                        st.text(f"📍 내 위치로부터 {dist_text}")

                    # 리스트 아이템에서 지도 포커스
                    if st.button("지도에서 보기", key=f"focus-{row['id']}"):
                        st.session_state["selected_bin_id"] = row["id"]
                        st.session_state["map_center"] = (row["lat"], row["lng"])
                        st.session_state["map_zoom"] = 18

            # 더 보기
            if len(filtered_disp) > limit:
                if st.button("더 보기", key="load_more"):
                    st.session_state["list_limit"] += 20
            else:
                st.caption("모든 휴지통 정보를 다 불러왔어요 🙂")

    with right:
        if filtered.empty:
            st.info("지도로 표시할 데이터가 없어요.", icon="ℹ️")
            return

        center = st.session_state.get("map_center", DEFAULT_CENTER)
        zoom = st.session_state.get("map_zoom", DEFAULT_ZOOM)

        # 내 위치가 있고, 아직 특정 휴지통을 선택하지 않았다면 내 위치를 중심으로
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
        )


if __name__ == "__main__":
    main()
