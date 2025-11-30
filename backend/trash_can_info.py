import requests
import os

ENDPOINT = 'http://api.data.go.kr/openapi/tn_pubr_public_trash_can_api'
SERVICE_KEY = os.environ.get('RECYCLE_INFO_KEY')

def fetch_trash_can_data(
    pageNo: int = 1,
    numOfRows: int = 10,
    type: str = "json", 

    INSTL_PLC_NM: str | None = None,      # 설치장소명
    CTPV_NM: str | None = None,          # 시도명
    SGG_NM: str | None = None,           # 시군구명
    LCTN_ROAD_NM: str | None = None,     # 소재지도로명주소
    LCTN_LOTNO_ADDR: str | None = None,  # 소재지지번주소
    LAT: str | None = None,              # 위도
    LOT: str | None = None,              # 경도
    ACTL_PSTN: str | None = None,        # 세부위치
    TRASH_CAN_KND: str | None = None,    # 휴지통종류
    MNG_INST_NM: str | None = None,      # 관리기관명
    MNG_INST_TELNO: str | None = None,   # 관리기관전화번호
):
    if not SERVICE_KEY:
        raise ValueError('환경 변수 - 휴지통 위치 서비스 KEY가 설정되지 않았어요')
    
    params = {
        'serviceKey': SERVICE_KEY,
        'pageNo': pageNo,
        'numOfRows':numOfRows,
        'type':type
    }

    optional_params = {
        'INSTL_PLC_NM': INSTL_PLC_NM,
        'CTPV_NM': CTPV_NM,
        'SGG_NM': SGG_NM,
        'LCTN_ROAD_NM': LCTN_ROAD_NM,
        'LCTN_LOTNO_ADDR': LCTN_LOTNO_ADDR,
        'LAT': LAT,
        'LOT': LOT,
        'ACTL_PSTN': ACTL_PSTN,
        'TRASH_CAN_KND': TRASH_CAN_KND,
        'MNG_INST_NM': MNG_INST_NM,
        'MNG_INST_TELNO': MNG_INST_TELNO,
    }

    # optional 값이 존재하면 params에 추가
    for key, value in optional_params.items():
        if value is not None and value != "":
            params[key] = value

    response = requests.get(ENDPOINT, params=params, timeout=5)
    response.raise_for_status()

    if type.lower() == "json":
        return response.json()
    else:
        return response.text
