import base64
import streamlit as st
from backend.call_custom_vision import call_custom_vision
from backend.call_openai_api import call_openai_api

FEEDBACK_URL = "https://github.com/EchoSongEEE/recycling-app/issues/new?title=[버그신고]&body=어떤+이미지에서+어떤+안내가+나왔는지+작성해주세요."

def page():
    st.title("♻️ 재활용 분리배출 코칭 시스템")
    st.write("이미지를 업로드하면, 어떤 품목인지 인식하고 분리배출 방법을 안내해 드려요.")

    # 세션 상태 초기화
    if "cv_result" not in st.session_state:
        st.session_state.cv_result = None
    if "guide" not in st.session_state:
        st.session_state.guide = None

    # 스타일 커스터마이징
    st.markdown(
        """
        <style>
        .main > div {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stButton > button {
            border-radius: 999px;
            padding: 0.5rem 1.5rem;
            border: 1px solid #e2e8f0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col_left, _, col_right = st.columns([1, 0.2, 2], vertical_alignment="top")

    # ----------------- 왼쪽 영역: 업로드 & 미리보기 -----------------
    with col_left:
        st.markdown("### 🌍 업로드 & 미리보기")

        video_html = """
        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;
                    border-radius: 16px; box-shadow: 0 6px 18px rgba(15, 23, 42, 0.15); margin-bottom: 1.5rem;">
          <iframe
                src="https://www.youtube.com/embed/9m4gnPozJVM?si=G129D9vIK55ic3kQ&autoplay=1&mute=1"
                title="기후에너지환경부 홍보 영상"
                frameborder="0"
                allow="autoplay; accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                referrerpolicy="strict-origin-when-cross-origin"
                allowfullscreen
                style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
          </iframe>
        </div>
        """
        st.markdown(video_html, unsafe_allow_html=True)
        st.caption("출처: 기후에너지환경부 YouTube 채널")

        uploaded_file = st.file_uploader(
            "재활용 쓰레기 이미지를 업로드하세요.",
            type=["jpg", "jpeg", "png"],
        )

        if uploaded_file is None:
            st.session_state.cv_result = None
            st.session_state.guide = None

        if uploaded_file is not None:
            img_left, img_center, img_right = st.columns([1, 3, 1])
            with img_center:
                st.image(uploaded_file, caption="업로드된 이미지", use_container_width=True)

            if st.button("분석 시작", use_container_width=True):
                with st.spinner("이미지 분석 중..."):
                    image_data = uploaded_file.read()
                    cv_result = call_custom_vision(image_data)

                if "error" in cv_result:
                    st.session_state.cv_result = cv_result
                    st.session_state.guide = None
                else:
                    tag = cv_result["tag"]
                    prob = cv_result["probability"]

                    with st.spinner("분리배출 방법 생성 중..."):
                        guide = call_openai_api(tag)

                    st.session_state.cv_result = cv_result
                    st.session_state.guide = guide
        else:
            st.info("이미지를 업로드한 후 **분석 시작** 버튼을 눌러 주세요 🙂")

    # ----------------- 오른쪽 영역: 분석 결과 -----------------
    with col_right:
        st.markdown("### 🔎 분석 결과")
        st.markdown(
            "<hr style='margin: 8px 0 16px; border: none; border-top: 1px solid #e2e8f0;'/>",
            unsafe_allow_html=True,
        )

        cv_result = st.session_state.cv_result
        guide = st.session_state.guide

        if cv_result is None:
            st.write("아직 분석 결과가 없습니다.")
        elif "error" in cv_result:
            st.error(f"Custom Vision 오류: {cv_result['error']}")
        else:
            tag = cv_result["tag"]
            prob = cv_result["probability"]
            prob_percent = prob * 100

            if prob_percent >= 95:
                mood_icon = "😄"
                mood_label = "Excellent"
                mood_color = "#38a169"
                bg_color = "#f0fff4"
                border_color = "#38a169"
                bar_color = "#48bb78"
            elif prob_percent >= 80:
                mood_icon = "😊"
                mood_label = "Good"
                mood_color = "#2b8a3e"
                bg_color = "#f0fff4"
                border_color = "#2b8a3e"
                bar_color = "#48bb78"
            elif prob_percent >= 60:
                mood_icon = "😐"
                mood_label = "Medium"
                mood_color = "#d69e2e"
                bg_color = "#fffaf0"
                border_color = "#d69e2e"
                bar_color = "#f6ad55"
            elif prob_percent >= 40:
                mood_icon = "😕"
                mood_label = "Poor"
                mood_color = "#dd6b20"
                bg_color = "#fff5f0"
                border_color = "#dd6b20"
                bar_color = "#ed8936"
            else:
                mood_icon = "😠"
                mood_label = "Very Bad"
                mood_color = "#e53e3e"
                bg_color = "#fff5f5"
                border_color = "#e53e3e"
                bar_color = "#fc8181"

            st.markdown(
                f"""
<div style="margin-top:1rem;display:flex;justify-content:flex-start;">
  <div style="
      flex:0 1 720px;
      padding:1.25rem 1.5rem;
      border-radius:1rem;
      background-color:{bg_color};
      border:1px solid {border_color};
      display:flex;
      gap:1rem;
      align-items:flex-start;">
    <div style="font-size:2.1rem;line-height:1.1;">{mood_icon}</div>
    <div style="flex:1;display:flex;flex-direction:column;gap:0.4rem;">
      <div style="font-size:0.9rem;color:#4a5568;">인식된 품목</div>
      <div style="font-size:1.6rem;font-weight:700;color:#22543d;">{tag}</div>
      <div style="display:flex;align-items:center;gap:0.6rem;margin-top:0.1rem;">
        <div style="font-size:0.95rem;color:#2f855a;">
          신뢰도: <strong>{prob_percent:.2f}%</strong>
        </div>
        <span style="
          font-size:0.8rem;
          font-weight:600;
          padding:0.15rem 0.7rem;
          border-radius:999px;
          background-color:#e6fffa;
          color:{mood_color};
          border:1px solid {mood_color};
        ">
          {mood_label}
        </span>
      </div>
      <div style="
          margin-top:0.6rem;
          width:100%;
          height:8px;
          background-color:#e2e8f0;
          border-radius:999px;
          overflow:hidden;">
        <div style="
            width:{prob_percent:.2f}%;
            height:100%;
            background-color:{bar_color};
            border-radius:999px;
            transition:width 0.4s ease;">
        </div>
      </div>
    </div>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

            st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
            st.markdown("### ✅ 분리배출 안내")
            st.markdown(
                "<hr style='margin: 8px 0 16px; border: none; border-top: 1px solid #e2e8f0;'/>",
                unsafe_allow_html=True,
            )

            if guide:
                st.write(guide)

                st.markdown("---")

            # 서비스 오류 신고 
            with st.expander("🚨 서비스 오류 / 잘못된 안내 신고하기"):
                st.write(
                    "AI가 잘못 안내했거나 서비스 오류가 있으면 아래 버튼을 눌러 알려주세요. "
                    "GitHub 이슈에 내용을 남기면 개발자가 확인 후 수정합니다."
                )
                st.link_button("GitHub로 신고하기", FEEDBACK_URL, use_container_width=True)
