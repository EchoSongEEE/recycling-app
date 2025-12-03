import streamlit as st
import pandas as pd
import pydeck as pdk

from backend.trash_can_info import fetch_trash_can_data

st.title("🗑️ 공공 휴지통 위치 조회 & 지도 보기")

st.caption("공공데이터 포털 휴지통 위치 정보를 기반으로, 지역/도로명/종류별 휴지통 위치를 조회하고 지도에서 확인할 수 있습니다.")

st.markdown("---")

with st.form("trash_can_search_form", clear_on_submit=False):
    st.subheader("1️⃣ 검색 조건 입력")

    col1, col2 = st.columns(2)

    with col1:
        ctpv_nm = st.text_input("시도명", placeholder="예: 서울특별시")
        sgg_nm = st.text_input("시군구명", placeholder="예: 종로구")

    with col2:
        road_addr = st.text_input("도로명 주소(일부)", placeholder="예: 사직로")
        trash_knd = st.text_input("휴지통 종류 (선택)", placeholder="예: 일반, 재활용 등")

    col_page = st.columns(2)
    with col_page[0]:
        page_no = st.number_input("페이지 번호", min_value=1, value=1, step=1)
    with col_page[1]:
        num_rows = st.slider("한 페이지 결과 수", min_value=10, max_value=200, value=50, step=10)

    submitted = st.form_submit_button("🔎 휴지통 위치 조회")

if submitted:
    try:
        with st.spinner("공공데이터에서 정보를 조회 중입니다..."):
            data = fetch_trash_can_data(
                pageNo=page_no,
                numOfRows=num_rows,
                type="json",
                CTPV_NM=ctpv_nm or None,
                SGG_NM=sgg_nm or None,
                LCTN_ROAD_NM=road_addr or None,
                TRASH_CAN_KND=trash_knd or None,
            )

        # --- JSON 파싱 ---
        body = data.get("response", {}).get("body", {})
        items = body.get("items")

        if isinstance(items, dict):
            items = items.get("item", [])
        if items is None:
            items = []

        if not items:
            st.warning("검색 조건에 해당하는 휴지통 위치를 찾지 못했습니다. 조건을 완화해서 다시 시도해 보세요.")
        else:
            df = pd.DataFrame(items)

            # 결과 개수 표시
            st.markdown("---")
            st.subheader("2️⃣ 조회 결과")

            result_count = len(df)
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.metric("조회된 휴지통 개수", f"{result_count} 개")
            with col_info2:
                st.write(
                    f"**필터** · 시도: `{ctpv_nm or '전체'}` / 시군구: `{sgg_nm or '전체'}` / 종류: `{trash_knd or '전체'}`"
                )

            # 탭으로 테이블 / 지도 나누기
            tab_table, tab_map = st.tabs(["📋 데이터 테이블", "🗺️ 지도에서 보기"])

            with tab_table:
                st.dataframe(
                    df[
                        [
                            "INSTL_PLC_NM",
                            "CTPV_NM",
                            "SGG_NM",
                            "LCTN_ROAD_NM",
                            "TRASH_CAN_KND",
                            "MNG_INST_NM",
                            "MNG_INST_TELNO",
                        ]
                    ],
                    use_container_width=True,
                )

            with tab_map:
                if {"LAT", "LOT"}.issubset(df.columns):
                    df_map = df[
                        [
                            "LAT",
                            "LOT",
                            "INSTL_PLC_NM",
                            "CTPV_NM",
                            "SGG_NM",
                            "LCTN_ROAD_NM",
                            "TRASH_CAN_KND",
                            "MNG_INST_NM",
                        ]
                    ].copy()

                    # 문자열 → 숫자 변환
                    df_map["LAT"] = pd.to_numeric(df_map["LAT"], errors="coerce")
                    df_map["LOT"] = pd.to_numeric(df_map["LOT"], errors="coerce")
                    df_map = df_map.dropna(subset=["LAT", "LOT"])
                    df_map = df_map.rename(columns={"LAT": "lat", "LOT": "lon"})

                    if df_map.empty:
                        st.info("위도/경도 정보가 없어 지도를 표시할 수 없습니다.")
                    else:
                        st.markdown("지도를 드래그/줌해서 위치를 자세히 볼 수 있습니다. 마커에 마우스를 올리면 상세 정보가 표시됩니다.")

                        layer = pdk.Layer(
                            "ScatterplotLayer",
                            df_map,
                            get_position="[lon, lat]",
                            get_radius=40,
                            get_fill_color=[0, 122, 255, 180],
                            pickable=True,
                        )

                        view_state = pdk.ViewState(
                            latitude=df_map["lat"].mean(),
                            longitude=df_map["lon"].mean(),
                            zoom=12,
                            pitch=0,
                        )

                        tooltip = {
                            "text": "설치장소: {INSTL_PLC_NM}\n"
                            "종류: {TRASH_CAN_KND}\n"
                            "주소: {LCTN_ROAD_NM}\n"
                            "관리기관: {MNG_INST_NM}"
                        }

                        st.pydeck_chart(
                            pdk.Deck(
                                layers=[layer],
                                initial_view_state=view_state,
                                tooltip=tooltip,
                            )
                        )
                else:
                    st.info("LAT / LOT 컬럼이 없어 지도 표시가 불가능합니다.")

    except Exception as e:
        st.error(f"API 호출 에러: {e}")
        with st.expander("🔎 상세 오류 보기"):
            st.exception(e)
