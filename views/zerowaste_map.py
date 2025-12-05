import streamlit as st
import pandas as pd
from backend.shop_finder import get_shops_by_location


def page():
    st.title("🌿 제로웨이스트 & 리필 스테이션 찾기")
    st.caption(
        "네이버 검색 API 기반 | 내 주변의 **친환경 가게**, **리필 스테이션**, **제로웨이스트 샵** "
        "정보를 지역명 기준으로 조회할 수 있습니다."
    )
    st.markdown("---")

    # 1. 검색 폼
    with st.form("shop_search_form", clear_on_submit=False):
        st.subheader("1️⃣ 검색 조건 입력")

        col1, col2 = st.columns([3, 1])
        with col1:
            # 지역명 입력 (예: 망원동, 강남구)
            region = st.text_input("지역명", placeholder="예: 망원동, 강남구, 서교동")
        with col2:
            st.write("")
            st.write("")

        submitted = st.form_submit_button("🔎 가게 찾기")

    # 2. 조회 로직
    if submitted:
        if not region:
            st.warning("지역명을 입력해주세요.")
            st.stop()

        try:
            with st.spinner(f"🔄 '{region}' 주변의 제로웨이스트 샵을 찾는 중..."):
                df = get_shops_by_location(region)

            if df.empty:
                st.warning(
                    "검색 조건에 해당하는 가게 정보가 없습니다. "
                    "(동네 이름을 정확히 입력했는지 확인해주세요)"
                )
                st.stop()

            rename_map = {
                "title": "가게명",
                "category": "카테고리",
                "address": "주소",
                "link": "상세링크",
            }

            # 필요한 경우 테이블용으로 쓸 수 있음 (지금은 카드 뷰 위주)
            df_display = df.rename(columns=rename_map)

            st.markdown("---")

            col_left, col_right = st.columns([4, 1])
            with col_left:
                st.subheader(f"2️⃣ 조회 결과: '{region}'")
            with col_right:
                st.caption(f"총 {len(df)}곳 발견")

            # 카드 레이아웃으로 결과 보여주기
            for idx, row in df.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])

                    with c1:
                        st.markdown(f"### {row['title']}")
                        st.caption(f"분류: {row['category']}")
                        st.markdown(f"**📍 주소:** {row['address']}")

                    with c2:
                        st.write("")
                        if row["link"]:
                            st.link_button(
                                "👉 링크 바로가기",
                                row["link"],
                                use_container_width=True,
                            )
                        else:
                            st.button(
                                "링크 없음",
                                disabled=True,
                                key=f"no_link_{idx}",
                            )

        except Exception as e:
            st.error(f"검색 중 오류가 발생했습니다: {e}")
            with st.expander("🔎 오류 상세"):
                st.exception(e)
