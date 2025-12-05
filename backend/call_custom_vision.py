import requests
import os

PREDICTION_KEY = os.environ.get("AZURE_CV_PREDICTION_KEY", "")
ENDPOINT_URL = os.environ.get("AZURE_CV_ENDPOINT", "")

def call_custom_vision(image_data: bytes) -> dict:
    if not image_data:
        return {"error": "이미지 데이터가 비어있습니다."}
    
    if not PREDICTION_KEY or not ENDPOINT_URL:
        return {"error": "AZURE_CV_PREDICTION_KEY 또는 AZURE_CV_ENDPOINT 환경 변수가 설정되지 않았습니다."}

    url = ENDPOINT_URL
    
    headers = {
        'Prediction-Key': PREDICTION_KEY,
        'Content-Type': 'application/octet-stream' 
    }
    
    try:
        response = requests.post(url, headers=headers, data=image_data)
        response.raise_for_status()

        result = response.json()
        
        if result.get('predictions'):
            best_prediction = max(result['predictions'], key=lambda x: x['probability'])
            tag_name = best_prediction['tagName']
            probability = best_prediction['probability']
            
            return {"tag": tag_name, "probability": probability}
        else:
            return {"error": "Custom Vision이 아무것도 인식하지 못했어요."}

    except requests.exceptions.RequestException as e:
        return {"error": f"Custom Vision API 호출 에러: {e}"}


try:
    with open("path/to/your/image.jpg", "rb") as f:
        sample_image_data = f.read()
    
    prediction_result = call_custom_vision(sample_image_data)
    print(prediction_result)
    
except FileNotFoundError:
    print("예시 이미지 파일을 찾을 수 없습니다. 실제 이미지 경로를 사용해 주세요.")