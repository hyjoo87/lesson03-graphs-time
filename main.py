import pandas as pd
import plotly.express as px
import streamlit as st

# =========================================================
# 0. 페이지 기본 설정
# =========================================================
st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", layout="wide")
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption("KOBIS 일별 박스오피스 데이터(최근 1년, 일별 TOP 10)를 시간 흐름으로 살펴보는 그래프 모음입니다.")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


# =========================================================
# 1. 데이터 불러오기
#    - @st.cache_data: 같은 데이터를 매번 새로 내려받지 않도록 캐시(임시 저장)해 둡니다.
# =========================================================
@st.cache_data
def load_data() -> pd.DataFrame:
    # '날짜' 열은 20250901 같은 8자리 숫자 형태이므로,
    # 먼저 문자열로 읽어온 뒤 진짜 날짜(datetime) 타입으로 바꿔줍니다.
    df = pd.read_csv(DATA_URL, dtype={"날짜": str})
    df["날짜"] = pd.to_datetime(df["날짜"], format="%Y%m%d")
    return df


df = load_data()


# =========================================================
# 2. 그래프마다 붙일 "이 그래프로 알 수 있는 것" 문구 자리
#    - 그래프를 추가할 때마다 이 함수를 재사용하면 됩니다.
# =========================================================
def insight_box(key: str, default_text: str = "") -> None:
    """그래프 바로 아래에, 그래프에서 읽어낸 점을 한 문장으로 적는 칸을 만듭니다."""
    st.text_area(
        "📝 이 그래프로 알 수 있는 것",
        value=default_text,
        placeholder="이 그래프를 보고 알게 된 점을 한 문장으로 적어보세요.",
        key=key,
        height=80,
    )


# =========================================================
# 구역 1. 영화별 일별 관객수 변화
#    - 드롭다운에서 영화를 고르면 해당 영화의 날짜별 일관객 변화를 선 그래프로 보여줍니다.
# =========================================================
st.header("1️⃣ 영화별 일별 관객수 변화")

movie_list = sorted(df["영화명"].unique())
selected_movie = st.selectbox("영화를 선택하세요", movie_list, key="movie_select_1")

# 선택한 영화의 데이터만 골라서 날짜 순서로 정렬합니다.
movie_df = df[df["영화명"] == selected_movie].sort_values("날짜")

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"'{selected_movie}' 일별 관객수 변화",
    labels={"날짜": "날짜", "일관객": "일일 관객 수(명)"},
)
# 마우스를 올렸을 때 날짜와 관객수가 보기 좋게 나오도록 설정합니다.
fig1.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>관객수: %{y:,}명<extra></extra>"
)
fig1.update_layout(hovermode="x unified")

st.plotly_chart(fig1, use_container_width=True)
insight_box("insight_1")

st.divider()

# =========================================================
# 구역 2. (다음 그래프를 추가할 자리)
#    - 새 그래프를 만들 때는 이 구역을 st.header(...)부터 복사해서 이어 붙이면 됩니다.
# =========================================================
st.header("2️⃣ 다음 그래프 (준비 중)")
st.info("여기에 두 번째 그래프를 추가할 예정입니다.")

st.divider()

# =========================================================
# 구역 3. (다음 그래프를 추가할 자리)
# =========================================================
st.header("3️⃣ 다음 그래프 (준비 중)")
st.info("여기에 세 번째 그래프를 추가할 예정입니다.")
