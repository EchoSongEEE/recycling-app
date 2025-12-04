# ♻️ 재활용 분리배출 코칭 시스템

Azure Custom Vision과 OpenAI GPT를 활용하여  
**재활용 쓰레기 이미지를 업로드하면 품목을 인식하고, 분리배출 방법을 자동으로 안내하는 웹 애플리케이션**입니다.

Streamlit 기반 UI를 활용해 간단한 이미지 업로드만으로 AI 기반 분리배출 가이드를 받을 수 있습니다.

<br />

## ✨ 주요 기능

- 🖼️ 이미지 업로드 기능 
- 🔍 Azure Custom Vision을 이용한 재활용 품목 인식
- 🧠 OpenAI GPT를 이용한 분리배출 가이드 생성
- 💬 사용자 친화적인 Streamlit UI 제공


<br />

## 🛠 기술 스택

- **Frontend/UI**
  - Streamlit (Python)

- **Backend/AI**
  - Azure Custom Vision (이미지 분류)
  - OpenAI GPT API (텍스트 생성)

- **기타**
  - Python 3.10+
  - python-dotenv, requests, openai


<br />

## 📁 폴더 구조

```
recycling-app/
  backend/
    __init__.py            # .env 로드 등 초기 설정
    call_custom_vision.py  # Azure Custom Vision 호출 모듈
    call_openai_api.py     # OpenAI GPT 호출 모듈
  .env                     # 환경 변수 설정 파일
  app.py                   # Streamlit 메인 애플리케이션
  requirements.txt         # 필요한 Python 패키지 목록
```
<br />

## 🚀 앱 실행 방법
  1. .env 파일이 제대로 설정되어 있는지 확인
  2. Streamlit 실행
```bash
    cd recycling-app
    streamlit run app.py
```
접속:
➡️ http://localhost:8501

<br />

## 🌊 프로젝트 플로우

```bash
[1] 사용자
    ↓ (이미지 업로드)

[2] Streamlit UI (app.py)
    ↓ 업로드된 파일을 읽어 바이너리로 변환

[3] backend.call_custom_vision
    ↓ 이미지 바이너리를 Azure Custom Vision API로 전송
    ↓ 가장 확률 높은 태그(tag) + probability 반환

[4] Streamlit UI
    ↓ "인식된 품목" 화면 표시
    ↓ 인식된 tag를 다음 단계로 전달

[5] backend.call_openai_api
    ↓ 태그를 기반으로 프롬프트 생성
    ↓ OpenAI GPT 모델 호출
    ↓ "3줄 분리배출 안내" 텍스트 반환

[6] Streamlit UI
    ↓ GPT가 생성한 가이드 표시
    ↓ 최종 사용자에게 전체 결과 제공
```
