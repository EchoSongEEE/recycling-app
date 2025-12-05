from openai import OpenAI
import os

AZURE_OPENAI_ENDPOINT = os.environ.get(
    "AZURE_OPENAI_ENDPOINT",
    "https://smu-team8-openai.openai.azure.com/openai/v1",
)
AZURE_OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = "gpt-4o-mini"

client = OpenAI(
    base_url=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
)


def call_openai_api(identified_tag: str) -> str:
    if not AZURE_OPENAI_API_KEY:
        return "OpenAI API Key 환경 변수가 설정되지 않아 정보를 생성할 수 없어요. .env 파일을 확인하세요."

    if not identified_tag:
        return "인식된 품목이 없어 분리수거 정보를 제공할 수 없어요."

    system_prompt = """
당신은 환경부의 공식적인 분리수거 전문가입니다.

역할:
- 사용자에게 분리수거 품목 이름을 받으면, 환경부 지침에 따라 분리수거 방법을 설명합니다.
- 오염/파손 여부와 관계없이, 핵심 분리수거 방법을 알려줍니다.
- 반드시 마크다운 형식으로만 답변합니다.

형식 규칙:
1. 첫 줄은 마크다운 h3 제목으로 작성합니다. (예: `### 플라스틱 용기 분리배출 방법`)
2. 제목 줄에는 아이콘이나 이모지를 넣지 않습니다.
3. 그 아래에는 총 5줄의 본문을 작성하여, 전체 6줄이 되도록 합니다.
4. 본문 각 줄은 한 문장씩 쓰고, 앞에 아이콘을 적절히 사용할 수 있습니다. (예: ♻️, 🧼, 🚮 등)
5. 중요한 키워드는 **굵게** 또는 *기울임*을 사용해 하이라이트합니다.
"""

    user_prompt = f"분리수거 품목: '{identified_tag}' 에 대한 분리수거 방법을 알려주세요."

    try:
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"❌ OpenAI API 호출 에러: {e}"
