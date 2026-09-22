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
# 구역 2. 일관객 합계 상위 5편의 날짜별 일관객 변화
#    - 전체 기간 동안 일관객을 합쳐서(총 누적이 아니라 일관객의 합) 가장 큰 5개 영화를 찾고,
#      그 5편을 한 그래프에 색으로 구분해서 보여줍니다.
# =========================================================
st.header("2️⃣ 일관객 합계 TOP 5 영화 비교")

# 영화명별로 '일관객'을 모두 더해서 합계가 큰 순서로 5편을 뽑습니다.
top5_movies = (
    df.groupby("영화명")["일관객"].sum().sort_values(ascending=False).head(5).index.tolist()
)

# 상위 5편에 해당하는 행만 골라서 날짜 순으로 정렬합니다.
top5_df = df[df["영화명"].isin(top5_movies)].sort_values("날짜")

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",  # 영화별로 다른 색의 선이 그려집니다.
    markers=True,
    title="일관객 합계 TOP 5 영화의 날짜별 일관객 변화",
    labels={"날짜": "날짜", "일관객": "일일 관객 수(명)", "영화명": "영화"},
)
fig2.update_traces(
    hovertemplate="%{fullData.name}<br>날짜: %{x|%Y-%m-%d}<br>관객수: %{y:,}명<extra></extra>"
)
fig2.update_layout(
    hovermode="x unified",
    legend_title_text="영화 (클릭하면 켜고 끌 수 있어요)",
)
# 플롯리는 기본적으로 범례를 클릭하면 해당 선을 껐다 켤 수 있습니다.

st.plotly_chart(fig2, use_container_width=True)
insight_box("insight_2")

st.divider()

# =========================================================
# 구역 3. 날짜별 10위권 전체 일관객 합계
#    - 하루 TOP 10에 든 영화들의 일관객을 모두 더해 그날의 전체 관객 규모를 영역 그래프로 봅니다.
#    - 합계가 가장 컸던 상위 3일을 그래프 위에 표시합니다.
# =========================================================
st.header("3️⃣ 날짜별 전체 관객수(TOP 10 합계) 흐름")

# 날짜별로 그날 10위권 영화들의 일관객을 모두 더합니다.
daily_total = df.groupby("날짜")["일관객"].sum().reset_index()

fig3 = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="날짜별 TOP 10 일관객 합계",
    labels={"날짜": "날짜", "일관객": "그날 TOP 10 관객 수 합계(명)"},
)
fig3.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>합계 관객수: %{y:,}명<extra></extra>"
)
fig3.update_layout(hovermode="x unified")

# 합계가 가장 컸던 3일을 찾아 그래프 위에 점과 날짜를 표시합니다.
top3_days = daily_total.sort_values("일관객", ascending=False).head(3)

fig3.add_scatter(
    x=top3_days["날짜"],
    y=top3_days["일관객"],
    mode="markers+text",
    text=top3_days["날짜"].dt.strftime("%Y-%m-%d"),
    textposition="top center",
    marker=dict(size=10, color="crimson"),
    name="합계 TOP 3일",
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>합계 관객수: %{y:,}명<extra></extra>",
)

st.plotly_chart(fig3, use_container_width=True)
insight_box("insight_3")

st.divider()

# =========================================================
# 구역 4. 일관객 합계 TOP 10 영화 (가로 막대그래프)
#    - 영화별 일관객 합계와, 그 영화가 10위권에 들었던 날수를 함께 보여줍니다.
# =========================================================
st.header("4️⃣ 일관객 합계 TOP 10 영화")

# 영화별로 일관객 합계와, 10위권에 든 날수(행 개수)를 함께 구합니다.
movie_summary = (
    df.groupby("영화명")
    .agg(일관객합계=("일관객", "sum"), 상위권일수=("날짜", "count"))
    .reset_index()
)

top10_summary = movie_summary.sort_values("일관객합계", ascending=False).head(10)
# 가로 막대그래프는 데이터의 첫 행이 아래쪽에, 마지막 행이 위쪽에 그려지므로
# 관객 수가 많은 영화가 위로 오도록 오름차순으로 다시 정렬합니다.
top10_summary = top10_summary.sort_values("일관객합계", ascending=True)

fig4 = px.bar(
    top10_summary,
    x="일관객합계",
    y="영화명",
    orientation="h",
    title="일관객 합계 TOP 10 영화",
    labels={"일관객합계": "일관객 합계(명)", "영화명": "영화"},
    custom_data=["상위권일수"],
)
fig4.update_traces(
    hovertemplate=(
        "%{y}<br>일관객 합계: %{x:,}명"
        "<br>10위권에 든 날수: %{customdata[0]}일<extra></extra>"
    )
)

st.plotly_chart(fig4, use_container_width=True)
insight_box("insight_4")
