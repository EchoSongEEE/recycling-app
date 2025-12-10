from openai import OpenAI
import os
import streamlit as st 

try:
    AZURE_OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"] 
except KeyError:
    AZURE_OPENAI_API_KEY = None

AZURE_OPENAI_ENDPOINT = os.environ.get(
    "AZURE_OPENAI_ENDPOINT",
    "https://smu-team8-openai.openai.azure.com/openai/v1",
)
AZURE_OPENAI_DEPLOYMENT = "gpt-4o-mini"

client = OpenAI(
    base_url=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
)


def call_openai_api(
    identified_tag: str,
    confidence: float | None = None,
    lang: str = "ko",
) -> str:
    # 1. API 키 확인
    if not AZURE_OPENAI_API_KEY:
        if lang == "en":
            return "OpenAI API key is not set. Please check your environment settings."
        return "OpenAI API Key 환경 변수가 설정되지 않아 정보를 생성할 수 없어요. .env 파일을 확인하세요."

    # 2. 태그 확인
    if not identified_tag:
        if lang == "en":
            return "No item was detected."
        return "인식된 품목이 없어 분리수거 정보를 제공할 수 없어요."

    # ───────────────── confidence 텍스트 준비 ─────────────────
    # 프롬프트에 들어갈 정확도 정보를 포맷팅합니다.
    conf_text_en = ""
    conf_text_ko = ""
    if confidence is not None:
        conf_text_en = f" (Confidence Score: {confidence:.2f})"
        conf_text_ko = f" (정확도: {confidence:.2f})"

    # ───────────────── 시스템 프롬프트 설정 (핵심 수정 부분) ─────────────────
    if lang == "en":
        system_prompt = """
You are a friendly and professional 'Recycling Coach' following standard Korean recycling guidelines.

# Task
Analyze the given waste item and its confidence score to provide proper disposal instructions.

# Logic based on Confidence Score
1. **Low (< 0.6)**: 
   - The image is unclear. Apologize and ask the user to retake the photo. 
   - **DO NOT** provide recycling steps.
   - Message: "Sorry, I can't clearly identify the item. 😥 Could you take a closer picture?"
2. **Medium (0.6 ~ 0.85)**: 
   - Unsure. Ask "Is this [Item Name]?" first. 
   - If yes, provide the recycling guide below.
3. **High (>= 0.85)**: 
   - Confident. Say "This is [Item Name]! 🙆‍♂️" and provide the recycling guide immediately.

# Output Format (Recycling Guide)
If the score is high enough to provide a guide, use this Markdown format:

## 🗑️ [Item Name] Disposal Guide
* **Empty/Rinse 🚿**: (Instructions on emptying and washing)
* **Remove/Separate ✂️**: (Instructions on removing labels, caps, etc.)
* **Crush/Compress 🦶**: (Instructions on reducing volume)
* **Disposal Location 📦**: (Where to put it: e.g., Transparent PET bin, General waste)

# Constraints
- Respond in Markdown.
- Use emojis to make it friendly.
"""
        user_prompt = (
            f"Item: '{identified_tag}'{conf_text_en}. "
            "Provide the recycling guide based on the confidence score."
        )

    else:
        # 한국어 프롬프트
        system_prompt = """
당신은 대한민국 환경부 지침을 따르는 '친절하고 꼼꼼한 분리배출 코치'입니다.

# 임무
사용자가 제공한 쓰레기 품목(Item)과 정확도(Confidence)를 분석하여 상황에 맞는 답변을 하세요.

# 정확도(Confidence)별 대응 로직
1. 낮음 (0.6 미만):
   - 행동: 분리배출 방법을 안내하지 마세요.
   - 메시지: "죄송합니다, 사진이 흔들렸거나 잘 보이지 않아 판단하기 어렵네요. 😥 물체가 잘 보이도록 다시 찍어주시겠어요?"

2. 중간 (0.6 이상 ~ 0.85 미만):
   - 행동: 추측이 맞는지 먼저 물어보세요.
   - 메시지: "혹시 이 물건이 [한국어 분류명] 맞나요? 🤔 맞다면 아래 방법대로 배출해 주세요!" (이후 가이드 출력)

3. 높음 (0.85 이상):
   - 행동: 확신을 가지고 바로 안내하세요.
   - 메시지: "이건 [한국어 분류명] 입니다! 🙆‍♂️ 이렇게 분리배출 하시면 완벽합니다." (이후 가이드 출력)

# 배출 가이드 출력 양식 (Markdown)
안내 시에는 반드시 아래 목차를 사용하여 구체적인 행동을 지시하세요.

## 🗑️ [한국어 분류] 배출 가이드
 비우기/헹구기 🚿: (내용물을 비우고 물로 씻어야 하는지 설명)
 분리하기 ✂️: (라벨, 뚜껑, 테이프 등 다른 재질 제거 여부)
 부피 줄이기 🦶: (찌그러뜨리거나 접어서 부피를 줄이는 방법)
 배출 장소 📦: (투명 페트병 전용, 캔류, 일반쓰레기 등 배출 위치)

# 제약 사항
- 입력된 품목 명(tag)이 영어라면 한국어로 자연스럽게 번역하세요 (예: cardboard -> 골판지 박스).
- 사용자가 헷갈릴 만한 부분(예: 씻어도 얼룩진 컵라면 용기 등)은 '💡 꿀팁'으로 한 줄 덧붙여주세요.

# [책임감 있는 AI - 공정성 원칙 적용]
1. 재질 중심 분석: 쓰레기의 브랜드(고가/저가)나 외관의 낡음 정도에 따라 차별적인 어조를 사용하지 마세요. 오직 '재질'과 '배출 방법'에만 집중하여 공평하게 정보를 제공하세요.
2. 편향 방지: 특정 지역이나 계층에서만 사용하는 용어보다는, 누구나 이해할 수 있는 표준어를 사용하세요.
"""
        user_prompt = (
            f"분리수거 품목: '{identified_tag}'{conf_text_ko}. "
            "이 정보와 정확도를 바탕으로 가이드를 제공해주세요."
        )

    try:
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3, # 설명서이므로 창의성을 낮춤
        )
        return response.choices[0].message.content

    except Exception as e:
        if lang == "en":
            return f"❌ OpenAI API call error: {e}"
        return f"❌ OpenAI API 호출 에러: {e}"