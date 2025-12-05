from __future__ import annotations

import json
from pathlib import Path

import folium
import pandas as pd
import streamlit as st
import streamlit as st
from streamlit_folium import st_folium


BASE_DIR = Path(__file__).resolve().parents[1]  
GEOJSON_PATH = BASE_DIR / "data/recycle_link" / "서울_자치구_경계_2017.geojson"
LINK_CSV_PATH = BASE_DIR / "data/recycle_link" / "폐기물_신청_링크.csv"

GU_NAME_KEY = "SIG_KOR_NM"  

st.set_page_config(
    page_title="쓰담 | 서울시 폐기물 신청 지도",
    page_icon="🌿",
    layout="wide",
)



@st.cache_data
def load_gu_links() -> dict[str, str]:
    df = pd.read_csv(LINK_CSV_PATH, encoding="utf-8-sig")
    if not {"자치구", "신청링크"}.issubset(df.columns):
        raise ValueError(f"CSV에 '자치구', '신청링크' 컬럼이 필요해요. 현재: {list(df.columns)}")

    df["자치구"] = df["자치구"].astype(str).str.strip()
    df["신청링크"] = df["신청링크"].astype(str).str.strip()
    return dict(zip(df["자치구"], df["신청링크"]))


@st.cache_data
def load_seoul_geojson() -> dict:
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def _get_feature_centroid(feature: dict) -> tuple[float, float] | None:
    geom = feature.get("geometry", {})
    gtype = geom.get("type")
    coords = geom.get("coordinates")

    if not coords:
        return None

    points = []

    try:
        if gtype == "Polygon":
            ring = coords[0]
            points = ring
        elif gtype == "MultiPolygon":
            ring = coords[0][0]
            points = ring
        else:
            return None
    except Exception:
        return None

    if not points:
        return None

    lngs = [p[0] for p in points]
    lats = [p[1] for p in points]

    center_lng = sum(lngs) / len(lngs)
    center_lat = sum(lats) / len(lats)
    return (center_lat, center_lng)


def create_seoul_map(geojson_data: dict, gu_links: dict[str, str]) -> folium.Map:

    m = folium.Map(
        location=(37.5665, 126.9780),
        zoom_start=11,
        tiles=None,
        zoom_control=True,
    )

    white_bg_css = """
    <style>
    .leaflet-container {
        background: #ffffff !important;
    }
    </style>
    """
    m.get_root().html.add_child(folium.Element(white_bg_css))


    for feat in geojson_data.get("features", []):
        props = feat.get("properties", {})
        gu_name = str(props.get(GU_NAME_KEY, "")).strip()
        url = gu_links.get(gu_name)

        if url:
            props["popup_html"] = (
                f"<b>{gu_name}</b><br/>"
                f'<a href="{url}" target="_blank" rel="noopener noreferrer">'
                "폐기물 신청 페이지 열기</a>"
            )
        else:
            props["popup_html"] = f"<b>{gu_name}</b><br/>등록된 신청 링크가 없습니다."

    def style_function(feature):
        return {
            "fillColor": "#f5f5f5",   
            "color": "#808080",      
            "weight": 1.5,
            "fillOpacity": 0.95,
        }

    def highlight_function(feature):
        return {
            "fillColor": "#93c5fd",   
            "color": "#2563eb",
            "weight": 2.5,
            "fillOpacity": 0.9,
        }

    # GeoJson 레이어
    gj = folium.GeoJson(
        geojson_data,
        name="서울 자치구",
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(
            fields=[GU_NAME_KEY],
            aliases=["자치구"],
            sticky=True,
            localize=True,
        ),
        popup=folium.GeoJsonPopup(
            fields=["popup_html"],
            labels=False,
            parse_html=True,
        ),
    )
    gj.add_to(m)

    # 서울 영역만 화면에 꽉 차게
    m.fit_bounds(gj.get_bounds())

    # 각 구 폴리곤 위에 이름 라벨 찍기 (항상 보이도록)
    for feat in geojson_data.get("features", []):
        props = feat.get("properties", {})
        gu_name = str(props.get(GU_NAME_KEY, "")).strip()
        center = _get_feature_centroid(feat)
        if center is None:
            continue

        folium.map.Marker(
            location=center,
            icon=folium.DivIcon(
                html=f"""
                <div style="
                    white-space: nowrap;
                    font-size:12px;
                    font-weight:600;
                    color:#222;
                    text-shadow: 0 0 3px rgba(255,255,255,1);
                ">
                    {gu_name}
                </div>
                """
            ),
        ).add_to(m)


    return m


def main():
    st.title("🗺️ 서울시 폐기물 신청 지도")
    st.caption(
        "구를 클릭하면 폐기물 신청 링크를 팝업으로 제공해요."
    )

    try:
        gu_links = load_gu_links()
        geojson_data = load_seoul_geojson()
    except Exception as e:
        st.error(f"데이터 불러오는 중 오류가 발생했어요: {e}")
        return

    seoul_map = create_seoul_map(geojson_data, gu_links)

    st_folium(
        seoul_map,
        width="100%",
        height=520,
    )

if __name__ == "__main__":
    main()
