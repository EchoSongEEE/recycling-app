import streamlit as st
from backend.call_custom_vision import call_custom_vision
from backend.call_openai_api import call_openai_api

# 페이지 기본 설정
st.set_page_config(
    page_title="재활용 분리배출 코치",
    page_icon="♻️",
    layout="centered",
)

st.title("♻️ 재활용 분리배출 코칭 시스템")
st.write("이미지를 업로드하면, 어떤 품목인지 인식하고 분리배출 방법을 안내해 드려요.")

# 이미지 업로드 UI
uploaded_file = st.file_uploader(
    "재활용 쓰레기 이미지를 업로드하세요.",
    type=["jpg", "jpeg", "png"],
)

if uploaded_file is not None:
    # 업로드된 이미지 미리보기
    st.image(uploaded_file, caption="업로드된 이미지", use_column_width=True)

    # 분석 실행
    if st.button("분석 시작"):
        with st.spinner("이미지 분석 중..."):
            image_data = uploaded_file.read()

            # Custom Vision 호출
            cv_result = call_custom_vision(image_data)

        if "error" in cv_result:
            st.error(f"Custom Vision 오류: {cv_result['error']}")
        else:
            tag = cv_result["tag"]
            prob = cv_result["probability"]

            st.success(f"인식된 품목: **{tag}**  (신뢰도: {prob:.2%})")

            # OpenAI 호출해서 분리배출 방법 받기
            with st.spinner("분리배출 방법 생성 중..."):
                guide = call_openai_api(tag)

            st.subheader("✅ 분리배출 안내")
            st.write(guide)
else:
    st.info("오른쪽 위 ‘Browse files’ 버튼을 눌러 이미지를 올려보세요 🙂")
