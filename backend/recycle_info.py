import requests
import os

BASE_URL = (
    'https://apis.data.go.kr/B552584/kecoapi/reutilCltRtrvlBzentyService/'
    'getReutilCltRtrvlBzentyInfo'
)
SERVICE_KEY = os.environ.get('RECYCLE_INFO_KEY')

def fetch_public_recycling_data(
    page_no: int = 1,          # 페이지 번호
    return_type: str = 'json', # json / xml
    knd_nm: str | None = None, # 종류
    rgn_nm: str | None = None, # 지역명
    addr: str | None = None,   # 주소(일부)
    timeout_sec: int = 15,     # 타임아웃(옵션)
):
    if not SERVICE_KEY:
        raise ValueError('환경 변수 RECYCLE_INFO_KEY가 설정되지 않았어요. .env를 확인해 주세요.')

    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': page_no,
        'numOfRows': 50,       # ← 한 페이지 결과 수 고정
        'returnType': return_type,
    }

    if knd_nm:
        params['kndNm'] = knd_nm
    if rgn_nm:
        params['rgnNm'] = rgn_nm
    if addr:
        params['addr'] = addr

    response = requests.get(BASE_URL, params=params, timeout=timeout_sec)
    response.raise_for_status()

    if return_type.lower() == 'json':
        return response.json()
    return response.text
