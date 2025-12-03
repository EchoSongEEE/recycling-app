import streamlit as st
import pandas as pd
from backend.recycle_info import fetch_public_recycling_data

st.title("♻️ 재활용 폐기물 수거·회수처 정보 조회")
st.caption(
    "한국환경공단 공공데이터 기반 | 폐휴대폰 · 중소폐가전 · 폐자동차의 "
    "수거·회수처 정보를 지역/주소/종류 조건으로 조회할 수 있습니다."
)
st.markdown("---")

with st.form("recycle_search_form", clear_on_submit=False):
    st.subheader("1️⃣ 검색 조건 입력")

    col1, col2 = st.columns(2)
    with col1:
        knd_nm = st.text_input("폐기물 종류", placeholder="폐휴대폰 / 중소폐가전 / 폐자동차")
        rgn_nm = st.text_input("지역명", placeholder="예: 서울특별시 강남구")
    with col2:
        addr = st.text_input("주소(일부)", placeholder="예: 테헤란로, 강남구 등")

    page_no = 1
    num_rows = 50  

    submitted = st.form_submit_button("🔎 조회하기")

if submitted:
    try:
        with st.spinner("🔄 한국환경공단 API에서 데이터를 가져오는 중..."):
            data = fetch_public_recycling_data(
            page_no=page_no,
            return_type='json',
            knd_nm=knd_nm or None,
            rgn_nm=rgn_nm or None,
            addr=addr or None,
        )


        body = data.get("body", {})
        items = body.get("items", [])

        if not isinstance(items, list):
            st.error("API 응답 구조가 다릅니다.")
            st.json(data)
            st.stop()

        if not items:
            st.warning("검색 조건에 해당하는 수거·회수처 정보가 없습니다.")
            st.stop()

        df = pd.DataFrame(items)

        rename_map = {
            "conmNm": "업체명",
            "kndNm": "폐기물 종류",
            "cltMthdNm": "수거방법",
            "rgnNm": "지역명",
            "addr": "주소",
            "telNo": "전화번호",
            "cltCstCn": "수거비용",
        }
        df = df.rename(columns=rename_map)

        st.markdown("---")

        col_left, col_right = st.columns([4, 1])
        with col_left:
            st.subheader("2️⃣ 조회 결과")
        with col_right:
            st.caption(f"{len(df)}개 / 총 {body.get('totalCount', '?')}개")

        st.dataframe(
            df,
            height=600,                # 표 높이 크게
            use_container_width=True,  # 전체 폭 사용
        )

        with st.expander("📦 원본 JSON 보기"):
            st.json(data)

    except Exception as e:
        st.error(f"API 호출 에러: {e}")
        with st.expander("🔎 오류 상세"):
            st.exception(e)
