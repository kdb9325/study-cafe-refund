"""
앤딩 스터디카페 환불 계산기 - Streamlit 웹 UI (모바일 최적화)
실행: streamlit run app.py
"""
import streamlit as st
from refund_calculator import (
    calculate_refund,
    calculate_extended_period_refund,
    PERIOD_PASS_REFUND_TABLE,
    TIME_PASS_PRICES,
    HOURLY_DEDUCTION,
    TIME_PASS_EXPIRY_DAYS,
    EXTENDED_REFUND_RATIOS,
)

st.set_page_config(
    page_title="앤딩 환불 계산기",
    page_icon="📚",
    layout="centered",
)

# ─── 모바일 최적화 CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
/* 전체 폰트 크기 및 여백 */
html, body, [class*="css"] {
    font-size: 16px;
}

/* 버튼 및 selectbox 터치 영역 확대 */
div[data-testid="stSelectbox"] > div,
div[data-testid="stNumberInput"] > div > div > input {
    font-size: 16px !important;
    min-height: 48px;
}

/* 메트릭 카드 스타일 */
div[data-testid="stMetric"] {
    background-color: #f8f9fa;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
}

div[data-testid="stMetric"] label {
    font-size: 13px !important;
    color: #666;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 22px !important;
    font-weight: 700;
}

/* 결과 박스 */
div[data-testid="stAlert"] {
    border-radius: 12px;
    font-size: 18px !important;
    font-weight: 600;
    padding: 16px;
}

/* 탭 터치 영역 */
button[data-baseweb="tab"] {
    font-size: 14px !important;
    padding: 10px 8px !important;
}

/* 슬라이더 */
div[data-testid="stSlider"] {
    padding: 8px 0;
}

/* 구분선 여백 */
hr {
    margin: 16px 0;
}
</style>
""", unsafe_allow_html=True)

st.title("📚 앤딩 환불 계산기")
st.caption("환불 규정에 따른 정확한 환불금액을 즉시 계산합니다.")
st.divider()

# ─── 탭 구성 ─────────────────────────────────────────────────────────────────
tab_period, tab_time, tab_extended, tab_rules = st.tabs(
    ["🗓 기간권", "⏱ 시간권", "📊 확장기간권", "📋 규정"]
)

# ─── 탭 1: 기간권 ────────────────────────────────────────────────────────────
with tab_period:
    st.subheader("기간권 환불")

    product_type_opt = st.selectbox(
        "상품 종류",
        ["기간권", "당일권 (환불 불가)", "스터디룸 (환불 불가, 일정 변경 가능)"],
        key="period_type",
    )

    if "환불 불가" in product_type_opt:
        if "스터디룸" in product_type_opt:
            st.warning("⚠️ 스터디룸은 환불이 불가합니다.\n예약 일정 변경만 가능합니다.")
        else:
            st.warning("⚠️ 당일권은 환불이 불가합니다.")
    else:
        product_name = st.selectbox(
            "기간권 종류",
            list(PERIOD_PASS_REFUND_TABLE.keys()),
            key="period_product",
        )

        info = PERIOD_PASS_REFUND_TABLE[product_name]
        total_days = info["total_weeks"] * 7

        st.metric("상품금액", f"{info['price']:,}원")
        st.metric("이용 가능 기간", f"최대 {total_days}일 ({info['total_weeks']}주)")

        usage_days = st.number_input(
            "사용일수 (일)",
            min_value=1,
            max_value=total_days,
            value=1,
            step=1,
            key="period_usage",
        )

        result = calculate_refund("기간권", product_name, int(usage_days))
        week_num = result.get("주차", (int(usage_days) - 1) // 7 + 1)

        st.divider()

        st.metric("사용 주차", f"{week_num}주차")
        st.metric(
            "환불금액",
            f"{result['환불금액']:,}원",
            delta=f"-{info['price'] - result['환불금액']:,}원 차감",
        )

        if result["환불가능"]:
            st.success(f"✅ 환불 가능: {result['환불금액']:,}원")
        else:
            st.error("❌ 환불 불가 (0원)")

        st.info(f"적용 규정: {result['사유']}")

# ─── 탭 2: 시간권 ────────────────────────────────────────────────────────────
with tab_time:
    st.subheader("시간권 환불")
    st.caption(f"시간당 {HOURLY_DEDUCTION:,}원 차감 | 구매 후 {TIME_PASS_EXPIRY_DAYS}일 초과 시 환불 불가")

    time_product = st.selectbox(
        "시간권 종류",
        list(TIME_PASS_PRICES.keys()),
        key="time_product",
    )

    price = TIME_PASS_PRICES[time_product]
    max_hours = price // HOURLY_DEDUCTION + 50

    usage_hours = st.number_input(
        "이용시간 (시간)",
        min_value=0,
        max_value=max_hours,
        value=0,
        step=1,
        key="time_usage",
    )

    days_since = st.number_input(
        "구매 후 경과 일수",
        min_value=0,
        max_value=365,
        value=0,
        step=1,
        key="time_days",
        help=f"구매 후 {TIME_PASS_EXPIRY_DAYS}일 초과 시 환불 불가",
    )

    result = calculate_refund(
        "시간권", time_product, int(usage_hours), days_since_purchase=int(days_since)
    )
    deduction = int(usage_hours) * HOURLY_DEDUCTION

    st.divider()

    st.metric("상품금액", f"{price:,}원")
    st.metric(
        "차감금액",
        f"{deduction:,}원",
        delta=f"{usage_hours}시간 × {HOURLY_DEDUCTION:,}원",
        delta_color="inverse",
    )
    st.metric("환불금액", f"{result['환불금액']:,}원")

    if days_since > TIME_PASS_EXPIRY_DAYS:
        st.error(f"❌ 환불 불가 — 구매 후 {TIME_PASS_EXPIRY_DAYS}일 초과")
    elif result["환불가능"]:
        st.success(f"✅ 환불 가능: {result['환불금액']:,}원")
    else:
        st.error("❌ 환불 불가 — 차감액이 상품금액 이상")

    st.info(f"계산식: {result['사유']}")

# ─── 탭 3: 확장 기간권 ───────────────────────────────────────────────────────
with tab_extended:
    st.subheader("확장 기간권 (2~20주)")
    st.markdown("전체 기간을 **4분기**로 균등 분할하여 **70% → 40% → 20% → 0%** 적용")

    total_weeks = st.slider("주권 기간 (주)", min_value=2, max_value=20, value=8)

    ext_price = st.number_input(
        "상품금액 (원)", min_value=1_000, value=100_000, step=1_000
    )

    max_ext_days = total_weeks * 7
    ext_usage = st.number_input(
        "사용일수 (일)",
        min_value=1,
        max_value=max_ext_days,
        value=1,
        step=1,
        key="ext_usage",
    )

    # 분기 구조 시각화 (2x2 그리드)
    st.markdown("**분기 구조**")
    quarter_size = total_weeks / 4
    icons = ["🟢", "🟡", "🟠", "🔴"]
    row1 = st.columns(2)
    row2 = st.columns(2)
    grid = [row1[0], row1[1], row2[0], row2[1]]

    for i, (cell, ratio, icon) in enumerate(zip(grid, EXTENDED_REFUND_RATIOS, icons)):
        q_start_w = round(i * quarter_size) + 1
        q_end_w   = round((i + 1) * quarter_size)
        label = f"{ratio * 100:.0f}% 환불" if ratio > 0 else "환불 불가"
        cell.metric(
            f"{icon} {i + 1}분기 ({q_start_w}~{q_end_w}주)",
            label,
        )

    st.divider()

    try:
        result = calculate_extended_period_refund(int(total_weeks), int(ext_price), int(ext_usage))

        st.metric("상품금액", f"{int(ext_price):,}원")
        st.metric("적용 분기 / 비율", f"{result['분기']}  |  {result['환불비율']}")
        st.metric("환불금액", f"{result['환불금액']:,}원")

        if result["환불가능"]:
            st.success(f"✅ 환불 가능: {result['환불금액']:,}원")
        else:
            st.error("❌ 환불 불가 (0원) — 4분기(마지막 분기) 해당")

        st.info(f"적용 규정: {result['사유']}")

    except ValueError as exc:
        st.error(f"입력 오류: {exc}")

# ─── 탭 4: 환불 규정 전체 보기 ───────────────────────────────────────────────
with tab_rules:
    st.subheader("환불 규정 전체")

    st.markdown("### 기간권")
    for name, info in PERIOD_PASS_REFUND_TABLE.items():
        with st.expander(f"**{name}** — {info['price']:,}원"):
            rows = []
            for i, (max_day, refund) in enumerate(info["brackets"]):
                prev = info["brackets"][i - 1][0] + 1 if i > 0 else 1
                if refund > 0:
                    rows.append(f"| {i + 1}주차 ({prev}~{max_day}일) | **{refund:,}원** |")
                else:
                    rows.append(f"| {i + 1}주차 이후 ({prev}일~) | **환불 불가** |")
            st.markdown("| 구간 | 환불금액 |\n|------|----------|\n" + "\n".join(rows))

    st.markdown("### 시간권")
    st.markdown(
        f"- 시간당 **{HOURLY_DEDUCTION:,}원** 차감 후 잔액 환급\n"
        f"- 구매 후 **{TIME_PASS_EXPIRY_DAYS}일** 초과 시 환불 불가\n"
        f"- 환불금액 = 상품금액 − (이용시간 × {HOURLY_DEDUCTION:,}원), 음수 시 0원"
    )
    rows = [f"| {name} | {price:,}원 |" for name, price in TIME_PASS_PRICES.items()]
    st.markdown("| 상품명 | 상품금액 |\n|--------|----------|\n" + "\n".join(rows))

    st.markdown("### 환불 불가 상품")
    st.markdown(
        "- **당일권**: 환불 불가\n"
        "- **스터디룸**: 환불 불가 (예약 일정 변경만 가능)"
    )

    st.markdown("### 확장 기간권 분기별 환불 비율")
    st.markdown(
        "2~20주권 범용: 전체 기간을 4분기로 균등 분할\n\n"
        "| 분기 | 환불비율 |\n|------|----------|\n"
        "| 1분기 | **70%** |\n"
        "| 2분기 | **40%** |\n"
        "| 3분기 | **20%** |\n"
        "| 4분기 | **환불 불가** |"
    )
