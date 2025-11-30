import streamlit as st
import pandas as pd
import pydeck as pdk

from backend.trash_can_info import fetch_trash_can_data

st.title("🗑️ 공공 휴지통 위치 조회 & 지도 보기")

st.markdown("시도 / 시군구 / 도로명 주소 일부로 휴지통 위치를 검색하고, 지도로 확인할 수 있습니다.")

# 검색 조건 입력
col1, col2 = st.columns(2)
with col1:
    ctpv_nm = st.text_input("시도명 (CTPV_NM 예: 서울특별시)")
    sgg_nm = st.text_input("시군구명 (SGG_NM 예: 종로구)")
with col2:
    road_addr = st.text_input("도로명 주소(일부) (LCTN_ROAD_NM)")
    trash_knd = st.text_input("휴지통 종류 (TRASH_CAN_KND, 선택)")

if st.button("휴지통 위치 조회"):
    try:
        data = fetch_trash_can_data(
            pageNo=1,
            numOfRows=10,
            type="json",
            CTPV_NM=ctpv_nm or None,
            SGG_NM=sgg_nm or None,
            LCTN_ROAD_NM=road_addr or None,
            TRASH_CAN_KND=trash_knd or None,
        )

        st.json(data)
        # # --- JSON 파싱 (공공데이터 구조 방어적으로 처리) ---
        # body = data.get("response", {}).get("body", {})
        # items = body.get("items")

        # if isinstance(items, dict):
        #     items = items.get("item", [])
        # if items is None:
        #     items = []

        # if not items:
        #     st.warning("조회 결과가 없습니다.")
        #     st.stop()

        # df = pd.DataFrame(items)

        # st.subheader("📋 조회 결과 테이블")
        # st.dataframe(df)

        # # --- 지도용 데이터 가공 ---
        # if {"LAT", "LOT"}.issubset(df.columns):
        #     df_map = df[[
        #         "LAT",
        #         "LOT",
        #         "INSTL_PLC_NM",
        #         "CTPV_NM",
        #         "SGG_NM",
        #         "LCTN_ROAD_NM",
        #         "TRASH_CAN_KND",
        #         "MNG_INST_NM",
        #     ]].copy()

        #     df_map["LAT"] = pd.to_numeric(df_map["LAT"], errors="coerce")
        #     df_map["LOT"] = pd.to_numeric(df_map["LOT"], errors="coerce")
        #     df_map = df_map.dropna(subset=["LAT", "LOT"])
        #     df_map = df_map.rename(columns={"LAT": "lat", "LOT": "lon"})

        #     if df_map.empty:
        #         st.info("위도/경도 정보가 없어 지도를 표시할 수 없습니다.")
        #         st.stop()

        #     st.subheader("🗺️ 지도에서 보기 (점 클릭/호버)")

        #     # PyDeck 지도 (마우스 호버로 정보 확인)
        #     layer = pdk.Layer(
        #         "ScatterplotLayer",
        #         df_map,
        #         get_position="[lon, lat]",
        #         get_radius=40,
        #         get_fill_color=[0, 122, 255, 180],
        #         pickable=True,
        #     )

        #     view_state = pdk.ViewState(
        #         latitude=df_map["lat"].mean(),
        #         longitude=df_map["lon"].mean(),
        #         zoom=12,
        #         pitch=0,
        #     )

        #     tooltip = {
        #         "text": "설치장소: {INSTL_PLC_NM}\n"
        #                 "종류: {TRASH_CAN_KND}\n"
        #                 "주소: {LCTN_ROAD_NM}\n"
        #                 "관리기관: {MNG_INST_NM}"
        #     }

        #     st.pydeck_chart(
        #         pdk.Deck(
        #             layers=[layer],
        #             initial_view_state=view_state,
        #             tooltip=tooltip,
        #         )
        #     )

        # else:
        #     st.info("LAT / LOT 컬럼이 없어 지도 표시가 불가능합니다.")

    except Exception as e:
        st.error(f"API 호출 에러: {e}")
