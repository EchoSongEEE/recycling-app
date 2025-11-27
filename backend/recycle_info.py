import requests
import os

BASE_URL = 'https://apis.data.go.kr/B552584/kecoapi/reutilCltRtrvlBzentyService/getReutilCltRtrvlBzentyInfo'
SERVICE_KEY = os.environ.get('RECYCLE_INFO_KEY')

def fetch_public_recycling_data(
        # 페이지 번호
        page_no: int = 1,
        # 한 페이지 결과 수
        num_of_rows: int = 10,
        # 데이터 반환 타입
        return_type: str = 'json',
        # 종류
        knd_nm: str | None = None,
        # 지역명
        rgn_nm: str | None = None,
        # 주소
        addr: str | None = None,
):
    if not SERVICE_KEY:
        raise ValueError('환경 변수 - 재활용 폐기물 수거회수처 정보 조회 서비스 KEY가 설정되지 않았어요.')
    
    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': page_no,
        'numOfRows': num_of_rows,
        'returnType': return_type
    }

    if knd_nm:
        params['kndNm'] = knd_nm
    if rgn_nm:
        params['rgnNm'] = rgn_nm
    if addr:
        params['addr'] = addr

    # 요청
    response = requests.get(BASE_URL, params=params, timeout=5)
    response.raise_for_status()

    if return_type.lower() == 'json':
        return response.json()
    else:
        return response.text
