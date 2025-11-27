import streamlit as st
from backend.recycle_info import fetch_public_recycling_data

st.title('한국환경공단_재활용 폐기물 수거회수처 정보 조회 서비스')

# 폐휴대폰, 중소폐가전, 폐자동차
knd_nm = st.text_input('종류')
rgn_nm = st.text_input('지역명')
addr = st.text_input('주소')

if st.button('조회하기'):
    try:
        data = fetch_public_recycling_data(
            page_no=1,
            num_of_rows=20,
            return_type='json',
            knd_nm=knd_nm or None,
            rgn_nm=rgn_nm or None,
            addr=addr or None
        )
        st.success('조회 성공!')
        st.json(data)
    except Exception as e:
        st.error(f'API 호출 에러: {e}')