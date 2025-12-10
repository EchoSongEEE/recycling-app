import streamlit as st
from backend.call_custom_vision import call_custom_vision
from backend.call_openai_api import call_openai_api

FEEDBACK_URL = (
    "https://github.com/EchoSongEEE/recycling-app/issues/new"
    "?title=[버그신고]&body=어떤+이미지에서+어떤+안내가+나왔는지+작성해주세요."
)

# ───────────────── 언어 옵션 ─────────────────

LANG_OPTIONS = {
    "한국어": "ko",
    "English": "en",
}

TEXTS = {
    "ko": {
        "title": "♻️ 재활용 분리배출 코칭",
        "subtitle": "이미지를 업로드하면, 어떤 품목인지 인식하고 분리배출 방법을 안내해 드려요.",
        "upload_section_title": "🌍 업로드 & 미리보기",
        "uploader_label": "재활용 쓰레기 이미지를 업로드하세요.",
        "uploaded_image_caption": "업로드된 이미지",
        "analyze_button": "분석 시작",
        "upload_hint": "이미지를 업로드한 후 **분석 시작** 버튼을 눌러 주세요 🙂",
        "video_caption": "출처: 기후에너지환경부 YouTube 채널",
        "result_section_title": "🔎 분석 결과",
        "no_result": "아직 분석 결과가 없습니다.",
        "error_prefix": "Custom Vision 오류",
        "recognized_item": "인식된 품목",
        "confidence": "신뢰도",
        "guide_section_title": "✅ 분리배출 안내",
        "feedback_expander": "🚨 서비스 오류 / 잘못된 안내 신고하기",
        "feedback_body": (
            "AI가 잘못 안내했거나 서비스 오류가 있으면 아래 버튼을 눌러 알려주세요. "
            "GitHub 이슈에 내용을 남기면 개발자가 확인 후 수정합니다."
        ),
        "feedback_button": "GitHub로 신고하기",
        "spinner_analyze": "이미지 분석 중...",
        "spinner_guide": "분리배출 방법 생성 중...",
        "warn_very_low": (
            "⚠️ AI 신뢰도가 낮은 결과입니다. 인식된 품목이 실제와 다를 수 있으니, "
            "이미지를 다시 찍거나 다른 각도에서 업로드해 주세요."
        ),
        "warn_mid": (
            "ℹ️ 신뢰도가 아주 높은 편은 아니에요. "
            "분리배출 전에 한 번 더 육안으로 확인해 주세요."
        ),
        "uploaded_image_label": "업로드된 이미지",
        "privacy_title": "🛡️ 개인정보 보호 및 보안, 공정성 방침 안내",
        "privacy_content": """
        <div style="font-size: 0.85rem; color: #666; line-height: 1.4;">
        <strong>1. 개인정보 보호 (Privacy)</strong><br>
        업로드한 이미지는 <strong>서버에 저장되지 않습니다.</strong> 
        AI 분석을 위해 메모리에서 일시적으로 사용된 후 <strong>즉시 자동 삭제</strong>됩니다.<br><br>
        <strong>2. 공정성 (Fairness)</strong><br>
        본 AI는 제품의 브랜드, 가격, 낡음 정도에 편견을 갖지 않고 
        오직 <strong>'재질'</strong>에 근거하여 공평하게 안내합니다.
        </div>
        """
    },
    "en": {
        "title": "♻️ AI-based Recycling Sorting Coach",
        "subtitle": "Upload a waste image and the AI will detect the item and guide you on how to recycle it properly.",
        "upload_section_title": "🌍 Upload & Preview",
        "uploader_label": "Upload a recycling waste image.",
        "uploaded_image_caption": "Uploaded Image",
        "analyze_button": "Start Analysis",
        "upload_hint": "Please upload an image and click **Start Analysis** 🙂",
        "video_caption": "Source: Ministry of Climate, Energy and Environment (Korea) YouTube Channel",
        "result_section_title": "🔎 Analysis Result",
        "no_result": "No analysis result yet.",
        "error_prefix": "Custom Vision Error",
        "recognized_item": "Detected Item",
        "confidence": "Confidence",
        "guide_section_title": "✅ Recycling Instructions",
        "feedback_expander": "🚨 Report service errors / incorrect guidance",
        "feedback_body": (
            "If the AI gives wrong instructions or the service breaks, "
            "click the button below to open a GitHub issue. The developer will review and fix it."
        ),
        "feedback_button": "Report on GitHub",
        "spinner_analyze": "Analyzing image...",
        "spinner_guide": "Generating recycling instructions...",
        "warn_very_low": (
            "⚠️ The AI confidence is low. The detected item may be incorrect. "
            "Please try taking the photo again or upload from another angle."
        ),
        "warn_mid": (
            "ℹ️ The confidence is not very high. "
            "Please double-check the item yourself before disposal."
        ),
        "uploaded_image_label": "Uploaded Image",
        "privacy_title": "🛡️ Privacy, Security & Fairness Policy  ",
        "privacy_content": """
        <div style="font-size: 0.85rem; color: #666; line-height: 1.4;">
        <strong>1. Privacy & Security</strong><br>
        Uploaded images are <strong>NOT saved</strong> on any server. 
        They are <strong>deleted immediately</strong> from memory after analysis.<br><br>
        <strong>2. Fairness</strong><br>
        This AI provides unbiased instructions based solely on <strong>materials</strong>, 
        regardless of brand, price, or condition.
        </div>
        """
    },
}

MOOD_LABELS = {
    "ko": {
        "excellent": "Excellent",
        "good": "Good",
        "medium": "Medium",
        "poor": "Poor",
        "very_bad": "Very Bad",
    },
    "en": {
        "excellent": "Excellent",
        "good": "Good",
        "medium": "Medium",
        "poor": "Poor",
        "very_bad": "Very Bad",
    },
}


def page():
    # ───────────────── 언어 선택 (사이드바) ─────────────────
    if "lang" not in st.session_state:
        st.session_state.lang = "ko"

    lang_label = st.sidebar.selectbox(
        "Language / 언어 선택",
        options=list(LANG_OPTIONS.keys()),
        index=0 if st.session_state.lang == "ko" else 1,
    )
    lang = LANG_OPTIONS[lang_label]
    st.session_state.lang = lang
    t = TEXTS[lang]

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

    # ───────────────── 제목 ─────────────────
    st.title(t["title"])
    st.write(t["subtitle"])

    col_left, _, col_right = st.columns([1, 0.2, 2], vertical_alignment="top")

    # ----------------- 왼쪽 영역: 업로드 & 미리보기 -----------------
    with col_left:
        st.markdown(f"### {t['upload_section_title']}")

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
        st.caption(t["video_caption"])

        uploaded_file = st.file_uploader(
            t["uploader_label"],
            type=["jpg", "jpeg", "png"],
        )

        with st.expander(t["privacy_title"], expanded=True): 
            st.markdown(t["privacy_content"], unsafe_allow_html=True)

        if uploaded_file is None:
            st.session_state.cv_result = None
            st.session_state.guide = None

        if uploaded_file is not None:
            # 파일 포인터에서 바이트로 읽어서 재사용
            image_bytes = uploaded_file.getvalue()

            img_left, img_center, img_right = st.columns([1, 3, 1])
            with img_center:
                st.image(
                    image_bytes,
                    caption=t["uploaded_image_caption"],
                    use_container_width=True,
                )

            if st.button(t["analyze_button"], use_container_width=True):
                with st.spinner(t["spinner_analyze"]):
                    cv_result = call_custom_vision(image_bytes)

                if "error" in cv_result:
                    st.session_state.cv_result = cv_result
                    st.session_state.guide = None
                
                else:
                    tag = cv_result["tag"]
                    prob = cv_result["probability"]  # 👈 0~1 사이 신뢰도

                    with st.spinner(t["spinner_guide"]):
                        try:
                            guide = call_openai_api(
                                identified_tag=tag,
                                confidence=prob,   # 👈 여기!
                                lang=lang,
                            )
                        except TypeError:
                            # (혹시 구버전 함수가 배포돼 있을 때 대비)
                            guide = call_openai_api(tag, lang=lang)

                    st.session_state.cv_result = cv_result
                    st.session_state.guide = guide
                

        else:
            st.info(t["upload_hint"])

    # ----------------- 오른쪽 영역: 분석 결과 -----------------
    with col_right:
        st.markdown(f"### {t['result_section_title']}")
        st.markdown(
            "<hr style='margin: 8px 0 16px; border: none; border-top: 1px solid #e2e8f0;'/>",
            unsafe_allow_html=True,
        )

        cv_result = st.session_state.cv_result
        guide = st.session_state.guide

        if cv_result is None:
            st.write(t["no_result"])
        elif "error" in cv_result:
            st.error(f"{t['error_prefix']}: {cv_result['error']}")
        else:
            tag = cv_result["tag"]
            prob = cv_result["probability"]
            prob_percent = prob * 100

            # 신뢰도 단계별 스타일
            if prob_percent >= 95:
                mood_key = "excellent"
                mood_icon = "😄"
                mood_color = "#38a169"
                bg_color = "#f0fff4"
                border_color = "#38a169"
                bar_color = "#48bb78"
            elif prob_percent >= 80:
                mood_key = "good"
                mood_icon = "😊"
                mood_color = "#2b8a3e"
                bg_color = "#f0fff4"
                border_color = "#2b8a3e"
                bar_color = "#48bb78"
            elif prob_percent >= 60:
                mood_key = "medium"
                mood_icon = "😐"
                mood_color = "#d69e2e"
                bg_color = "#fffaf0"
                border_color = "#d69e2e"
                bar_color = "#f6ad55"
            elif prob_percent >= 40:
                mood_key = "poor"
                mood_icon = "😕"
                mood_color = "#dd6b20"
                bg_color = "#fff5f0"
                border_color = "#dd6b20"
                bar_color = "#ed8936"
            else:
                mood_key = "very_bad"
                mood_icon = "😠"
                mood_color = "#e53e3e"
                bg_color = "#fff5f5"
                border_color = "#e53e3e"
                bar_color = "#fc8181"

            mood_label = MOOD_LABELS[lang][mood_key]

            # 메인 카드
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
      <div style="font-size:0.9rem;color:#4a5568;">{t['recognized_item']}</div>
      <div style="font-size:1.6rem;font-weight:700;color:#22543d;">{tag}</div>
      <div style="display:flex;align-items:center;gap:0.6rem;margin-top:0.1rem;">
        <div style="font-size:0.95rem;color:#2f855a;">
          {t['confidence']}: <strong>{prob_percent:.2f}%</strong>
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

            # 신뢰도 낮을 때 경고 메시지
            if prob_percent < 40:
                st.warning(t["warn_very_low"])
            elif prob_percent < 60:
                st.info(t["warn_mid"])

            st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
            st.markdown(f"### {t['guide_section_title']}")
            st.markdown(
                "<hr style='margin: 8px 0 16px; border: none; border-top: 1px solid #e2e8f0;'/>",
                unsafe_allow_html=True,
            )

            if guide:
                st.write(guide)

            st.markdown("---")

        # ----------------- 서비스 오류 신고 -----------------
        with st.expander(t["feedback_expander"]):
            st.write(t["feedback_body"])
            st.link_button(
                t["feedback_button"],
                FEEDBACK_URL,
                use_container_width=True,
            )
