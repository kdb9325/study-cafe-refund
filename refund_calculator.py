"""
앤딩 스터디카페 환불 계산 모듈
환불 규정에 따른 정확한 환불금액 계산

데이터 출처: 환불표.xlsx (data_loader.py 를 통해 로드)
환불표.xlsx 를 수정하면 자동으로 이 모듈에 반영됩니다.
"""
from data_loader import (
    load_period_pass_table,
    load_time_pass_prices,
    HOURLY_DEDUCTION,
    TIME_PASS_EXPIRY_DAYS,
)

# ─── 엑셀에서 데이터 로드 ────────────────────────────────────────────────────
PERIOD_PASS_REFUND_TABLE: dict = load_period_pass_table()
TIME_PASS_PRICES: dict = load_time_pass_prices()

# ─── 확장 기간권 분기별 환불 비율 (70% / 40% / 20% / 0%) ─────────────────────
# 전체 기간을 4분기로 균등 분할하여 각 분기별 환불비율 적용
EXTENDED_REFUND_RATIOS: list = [0.70, 0.40, 0.20, 0.00]
EXTENDED_QUARTER_LABELS: list = ["1분기 (70%)", "2분기 (40%)", "3분기 (20%)", "4분기 (0%)"]


# ─── 내부 헬퍼 함수 ──────────────────────────────────────────────────────────

def _week_number(usage_days: int) -> int:
    """사용일수를 주차(1-based)로 변환. 예: 1~7일 → 1주차, 8~14일 → 2주차"""
    return (usage_days - 1) // 7 + 1


def _get_period_refund(product_name: str, usage_days: int) -> dict:
    """
    정의된 기간권 상품의 환불금액 계산.

    Parameters
    ----------
    product_name : str  상품명 (예: "4주권")
    usage_days   : int  사용일수 (1 이상)

    Returns
    -------
    dict  {"환불금액", "환불가능", "사유", "상품금액", "주차"}
    """
    if product_name not in PERIOD_PASS_REFUND_TABLE:
        raise ValueError(f"알 수 없는 기간권 상품: '{product_name}'\n"
                         f"사용 가능 상품: {list(PERIOD_PASS_REFUND_TABLE.keys())}")

    info = PERIOD_PASS_REFUND_TABLE[product_name]
    total_days = info["total_weeks"] * 7

    if usage_days < 1:
        raise ValueError("사용일수는 1 이상이어야 합니다.")
    if usage_days > total_days:
        raise ValueError(
            f"사용일수({usage_days}일)가 상품 전체 기간({total_days}일)을 초과합니다."
        )

    week_num = _week_number(usage_days)

    # 브라켓 순서대로 탐색 → 첫 번째 매칭(usage_days ≤ max_day) 적용
    for max_day, refund in info["brackets"]:
        if usage_days <= max_day:
            refundable = refund > 0
            reason = (
                f"{week_num}주차 사용 → {refund:,}원 환불"
                if refundable
                else f"{week_num}주차 이후 → 환불 불가"
            )
            return {
                "환불금액": refund,
                "환불가능": refundable,
                "사유": reason,
                "상품금액": info["price"],
                "주차": week_num,
            }

    # 안전망 (브라켓이 모든 범위를 커버하지 못하는 경우)
    return {
        "환불금액": 0,
        "환불가능": False,
        "사유": "환불 가능 기간 초과",
        "상품금액": info["price"],
        "주차": week_num,
    }


def _get_time_pass_refund(
    product_name: str, usage_hours: int, days_since_purchase: int = 0
) -> dict:
    """
    시간권 환불금액 계산.
    환불금액 = 상품금액 - (이용시간 × 1,500원), 음수면 0원 처리.
    구매 후 28일 초과 시 환불 불가.

    Parameters
    ----------
    product_name        : str  시간권 상품명
    usage_hours         : int  이용시간 (시간 단위)
    days_since_purchase : int  구매 후 경과 일수 (기본 0)

    Returns
    -------
    dict  {"환불금액", "환불가능", "사유", "상품금액"}
    """
    if product_name not in TIME_PASS_PRICES:
        raise ValueError(f"알 수 없는 시간권 상품: '{product_name}'\n"
                         f"사용 가능 상품: {list(TIME_PASS_PRICES.keys())}")
    if usage_hours < 0:
        raise ValueError("이용시간은 0 이상이어야 합니다.")

    price = TIME_PASS_PRICES[product_name]

    # 구매 후 28일 초과 시 환불 불가 규정
    if days_since_purchase > TIME_PASS_EXPIRY_DAYS:
        return {
            "환불금액": 0,
            "환불가능": False,
            "사유": f"구매 후 {TIME_PASS_EXPIRY_DAYS}일 초과 → 환불 불가",
            "상품금액": price,
        }

    # 환불금액 = 상품금액 - 이용시간 × 1,500원 (음수 시 0원)
    deduction = usage_hours * HOURLY_DEDUCTION
    refund = max(0, price - deduction)

    if refund > 0:
        reason = (
            f"상품금액 {price:,}원 - {usage_hours}시간 × {HOURLY_DEDUCTION:,}원 "
            f"= {refund:,}원"
        )
    else:
        reason = (
            f"차감액({deduction:,}원)이 상품금액({price:,}원) 이상 → 환불 불가"
        )

    return {
        "환불금액": refund,
        "환불가능": refund > 0,
        "사유": reason,
        "상품금액": price,
    }


# ─── 공개 API ─────────────────────────────────────────────────────────────────

def calculate_refund(
    product_type: str, product_name: str, usage: int, **kwargs
) -> dict:
    """
    통합 환불 계산 진입점.

    Parameters
    ----------
    product_type : str
        "기간권", "시간권", "당일권", "스터디룸" 중 하나
    product_name : str
        상품명 문자열 (예: "4주권", "100시간권")
    usage : int
        기간권 → 사용일수 (일, 1 이상)
        시간권 → 이용시간 (시간, 0 이상)
    **kwargs
        days_since_purchase (int): 시간권 구매 후 경과 일수 (기본 0)

    Returns
    -------
    dict
        {
            "환불금액": int,    # 원 단위 정수
            "환불가능": bool,
            "사유":     str,
            "상품금액": int,    # (해당되는 경우)
            "주차":     int,    # 기간권에만 포함
        }
    """
    pt = product_type.strip()

    if pt == "기간권":
        return _get_period_refund(product_name, usage)

    elif pt == "시간권":
        days_since_purchase = int(kwargs.get("days_since_purchase", 0))
        return _get_time_pass_refund(product_name, usage, days_since_purchase)

    elif pt in ("당일권", "스터디룸"):
        # 환불 불가 상품
        extra = " (예약 일정 변경만 가능)" if pt == "스터디룸" else ""
        return {
            "환불금액": 0,
            "환불가능": False,
            "사유": f"{pt}은(는) 환불 불가 상품입니다{extra}.",
        }

    else:
        raise ValueError(
            f"알 수 없는 상품 종류: '{product_type}'\n"
            f"사용 가능 종류: 기간권, 시간권, 당일권, 스터디룸"
        )


def calculate_extended_period_refund(
    total_weeks: int, price: int, usage_days: int
) -> dict:
    """
    2~20주권 범용 환불 계산 (확장 기능).
    전체 기간을 4분기로 균등 분할 후 70% / 40% / 20% / 0% 비율 적용.
    환불금액은 100원 단위 반올림.

    Parameters
    ----------
    total_weeks : int  전체 주권 기간 (2~20주)
    price       : int  상품금액 (원)
    usage_days  : int  사용일수 (1 이상)

    Returns
    -------
    dict
        {
            "환불금액": int,
            "환불가능": bool,
            "사유":     str,
            "상품금액": int,
            "주차":     int,
            "분기":     str,    # "1분기 (70%)" 등
            "환불비율": str,    # "70%" 등
        }
    """
    if not (2 <= total_weeks <= 20):
        raise ValueError("주권 기간은 2~20주 사이여야 합니다.")
    if price <= 0:
        raise ValueError("상품금액은 양수여야 합니다.")
    if usage_days < 1:
        raise ValueError("사용일수는 1 이상이어야 합니다.")

    total_days = total_weeks * 7
    if usage_days > total_days:
        raise ValueError(
            f"사용일수({usage_days}일)가 상품 기간({total_days}일)을 초과합니다."
        )

    week_num = _week_number(usage_days)

    # 전체 주수를 4분기로 균등 분할 (소수 허용)
    quarter_size = total_weeks / 4  # 분기당 주 수
    # 0-indexed 분기 번호 결정 (week_num 1-based → 0-based 변환 후 분기 계산)
    quarter_idx = min(int((week_num - 1) / quarter_size), 3)

    ratio = EXTENDED_REFUND_RATIOS[quarter_idx]
    label = EXTENDED_QUARTER_LABELS[quarter_idx]

    # 100원 단위 반올림 (실무 관행)
    refund = round(price * ratio / 100) * 100

    refundable = refund > 0
    reason = (
        f"{total_weeks}주권 {week_num}주차 ({label}) → {refund:,}원 환불"
        if refundable
        else f"{total_weeks}주권 {week_num}주차 ({label}) → 환불 불가"
    )

    return {
        "환불금액": refund,
        "환불가능": refundable,
        "사유": reason,
        "상품금액": price,
        "주차": week_num,
        "분기": label,
        "환불비율": f"{ratio * 100:.0f}%",
    }
