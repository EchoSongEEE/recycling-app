# backend/trash_can_info.py

from __future__ import annotations

import glob
import math
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Literal, Optional

import pandas as pd

GuName = Literal["마포구", "구로구", "노원구", "서초구", "성북구", "중랑구"]


@dataclass
class TrashCan:
    id: str
    gu: GuName
    name: str
    road_address: Optional[str]
    jibun_address: Optional[str]
    lat: float
    lng: float
    detail: Optional[str] = None
    type: Optional[str] = None


# CSV → 공통 컬럼명 매핑 후보
COL_MAP = {
    "gu": ["시군구명", "자치구명", "구명"],
    "name": ["설치장소명", "휴지통설치장소", "설치 장소명"],
    "road_address": ["소재지도로명주소", "도로명주소"],
    "jibun_address": ["소재지지번주소", "지번주소"],
    "lat": ["위도", "Y좌표", "Y좌표(WGS84)"],
    "lng": ["경도", "X좌표", "X좌표(WGS84)"],
    "detail": ["상세위치", "세부위치", "비고"],
    "type": ["휴지통종류", "용도구분"],
}


def _find_first_existing_column(df: pd.DataFrame, candidates: Iterable[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for key, candidates in COL_MAP.items():
        col = _find_first_existing_column(df, candidates)
        if col:
            rename_map[col] = key

    df = df.rename(columns=rename_map)

    # 위도/경도 필수
    if "lat" not in df.columns or "lng" not in df.columns:
        raise ValueError("위도/경도 컬럼을 찾을 수 없어요. CSV 컬럼명을 확인해 주세요.")

    # 필요한 컬럼만 추출 (없으면 NaN으로 채워짐)
    needed_cols = ["gu", "name", "road_address", "jibun_address", "lat", "lng", "detail", "type"]
    for c in needed_cols:
        if c not in df.columns:
            df[c] = None

    df = df[needed_cols]

    # 숫자 변환
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lng"] = pd.to_numeric(df["lng"], errors="coerce")
    df = df.dropna(subset=["lat", "lng"])

    # 구 필터 (우리가 쓸 6개만)
    valid_gu = {"마포구", "구로구", "노원구", "서초구", "성북구", "중랑구"}
    df = df[df["gu"].isin(valid_gu)]

    # 인덱스로 id 생성
    df = df.reset_index(drop=True)
    df["id"] = df.index.map(lambda i: f"{df.loc[i, 'gu']}-{i}")

    # 컬럼 순서 정리
    df = df[["id"] + needed_cols]

    return df


@lru_cache(maxsize=1)
def load_trash_cans() -> pd.DataFrame:
    """
    data/trash 폴더 내의 모든 CSV를 읽어서 하나의 DataFrame으로 합친다.
    """
    csv_paths = glob.glob("data/trash/*.csv")
    if not csv_paths:
        raise FileNotFoundError("data/trash/*.csv 경로에서 CSV 파일을 찾을 수 없어요.")

    frames = []
    for path in csv_paths:
        try:
            df_raw = pd.read_csv(path, encoding="utf-8-sig")
        except UnicodeDecodeError:
            df_raw = pd.read_csv(path, encoding="cp949")
        df_norm = _normalize_dataframe(df_raw)
        frames.append(df_norm)

    all_df = pd.concat(frames, ignore_index=True)
    # 혹시 중복 id가 있으면 제거
    all_df = all_df.drop_duplicates(subset=["id"]).reset_index(drop=True)
    return all_df


def get_trash_cans() -> pd.DataFrame:
    """외부에서 사용할 때는 항상 복사본을 반환 (원본 보호)."""
    return load_trash_cans().copy()


def filter_by_gu(df: pd.DataFrame, gu: Optional[GuName | str]) -> pd.DataFrame:
    if gu is None or gu == "전체":
        return df
    return df[df["gu"] == gu]


def search_by_keyword(df: pd.DataFrame, keyword: str) -> pd.DataFrame:
    if not keyword:
        return df

    kw = keyword.strip().lower()
    if not kw:
        return df

    # 설치장소명 + 도로명 + 지번 합쳐서 검색
    target = (
        df["name"].fillna("")
        + " "
        + df["road_address"].fillna("")
        + " "
        + df["jibun_address"].fillna("")
    ).str.lower()

    mask = target.str.contains(kw)
    return df[mask]


# ---- 위치 기반 기능 ----

EARTH_RADIUS = 6371000.0  # meters


def _deg2rad(deg: float) -> float:
    return deg * math.pi / 180.0


def haversine_distance_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    두 점 사이의 거리(미터) - 하버사인 공식.
    """
    d_lat = _deg2rad(lat2 - lat1)
    d_lng = _deg2rad(lng2 - lng1)

    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(_deg2rad(lat1)) * math.cos(_deg2rad(lat2)) * math.sin(d_lng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS * c


def annotate_distance(
    df: pd.DataFrame,
    center_lat: float,
    center_lng: float,
    col_name: str = "distance_m",
) -> pd.DataFrame:
    """
    주어진 중심점으로부터의 거리를 계산해 DataFrame에 추가한다.
    """
    df = df.copy()
    df[col_name] = df.apply(
        lambda row: haversine_distance_m(center_lat, center_lng, row["lat"], row["lng"]),
        axis=1,
    )
    return df


def find_nearby(
    df: pd.DataFrame,
    center_lat: float,
    center_lng: float,
    radius_m: float = 300.0,
    limit: Optional[int] = 50,
) -> pd.DataFrame:
    """
    중심점 반경 radius_m 이내의 휴지통만 필터링하고, 가까운 순으로 정렬.
    """
    df_dist = annotate_distance(df, center_lat, center_lng)
    df_dist = df_dist[df_dist["distance_m"] <= radius_m]
    df_dist = df_dist.sort_values("distance_m")

    if limit is not None:
        df_dist = df_dist.head(limit)

    return df_dist
