import requests
import os

PREDICTION_KEY = os.environ.get("AZURE_CV_PREDICTION_KEY")
ENDPOINT = os.environ.get("AZURE_CV_ENDPOINT")
PROJECT_ID = "YOUR_PROJECT_ID" # Azure Custom Vision 프로젝트 ID
PUBLISHED_ITERATION_NAME = "Iteration1" # 학습시킨 모델 버전 이름

def call_custom_vision(image_data):
    # 이미지 데이터를 Azure Custom Vision API로 전송하고 예측 태그 반환
    if not image_data:
        return {"error": "이미지 데이터가 비어있습니다."}

    # Custom Vision API URL 
    url = f"{ENDPOINT}customvision/v3.0/Prediction/{PROJECT_ID}/classify/iterations/{PUBLISHED_ITERATION_NAME}/image"
    
    # 헤더 설정: API 키와 이미지 형식 명시
    headers = {
        'Prediction-Key': PREDICTION_KEY,
        'Content-Type': 'application/octet-stream' # 바이너리 이미지 데이터 형식
    }
    
    try:
        # POST: 이미지 데이터를 전송
        response = requests.post(url, headers=headers, data=image_data)
        response.raise_for_status() # HTTP 오류가 발생 예외 처리

        result = response.json()
        
        # 가장 높은 확률 태그를 추출
        if result.get('predictions'):
            best_prediction = max(result['predictions'], key=lambda x: x['probability'])
            tag_name = best_prediction['tagName']
            probability = best_prediction['probability']
            
            # 예측 결과를 딕셔너리 형태로 반환
            return {"tag": tag_name, "probability": probability}
        else:
            return {"error": "Custom Vision이 아무것도 인식하지 못했어요."}

    except requests.exceptions.RequestException as e:
        return {"error": f"Custom Vision API 호출 에러: {e}"}

