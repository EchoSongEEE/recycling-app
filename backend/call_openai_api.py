import openai
import os

# .env 
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# OpenAI 클라이언트 초기화
client = openai.OpenAI(api_key=OPENAI_API_KEY)


def call_openai_api(identified_tag):
    # 환경 변수 누락 시 에러 처리
    if not OPENAI_API_KEY:
        return "OpenAI API Key 환경 변수가 설정되지 않아 정보를 생성할 수 없어요. .env 파일을 확인하세요."

    if not identified_tag:
        return "인식된 품목이 없어 분리수거 정보를 제공할 수 없어요."

    # 시스템 프롬프트: 모델의 역할과 제약 사항을 정의
    system_prompt = (
        "당신은 환경부의 공식적인 분리수거 전문가입니다. "
        "사용자에게 분리수거 품목을 받으면, 환경부 지침에 의거하여 분리수거 방법을 3줄로 명확히 요약하여 제공해야 합니다. "
        "오염/파손 여부와 관계없이 핵심 분리수거 방법을 알려주세요."
    )
    
    # 사용자 프롬프트: Custom Vision의 결과를 포함하여 질문
    user_prompt = f"분리수거 품목: '{identified_tag}' 에 대한 분리수거 방법을 알려주세요."

    try:
        # GPT 모델 호출 
        response = client.chat.completions.create(
            # TODO: model 이름
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3, # 낮은 온도 -> 일관되고 사실적인 답변 유도
        )
        
        # GPT가 생성한 텍스트 답변 추출
        gpt_response_text = response.choices[0].message.content
        return gpt_response_text
        
    except openai.APIError as e:
        # OpenAI API 호출 자체 에러
        return f"❌ OpenAI API 에러: status {e.status_code}. message: {e.response.text}"
    except Exception as e:
        # 기타 오류
        return f"❌ API 호출 에러: {e}"