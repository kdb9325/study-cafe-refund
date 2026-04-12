"""
앤딩 스터디카페 환불 계산기 - CLI 인터페이스
실행: python main.py
"""
from refund_calculator import (
    calculate_refund,
    calculate_extended_period_refund,
    PERIOD_PASS_REFUND_TABLE,
    TIME_PASS_PRICES,
    TIME_PASS_EXPIRY_DAYS,
)


# ─── 출력 유틸리티 ────────────────────────────────────────────────────────────

def divider(char: str = "─", width: int = 44) -> None:
    print(char * width)


def select_from_menu(title: str, options: list) -> int:
    """번호 메뉴를 출력하고 유효한 선택 번호(1-based)를 반환."""
    print(f"\n{title}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        raw = input("\n선택: ").strip()
        if raw.isdigit():
            choice = int(raw)
            if 1 <= choice <= len(options):
                return choice
        print(f"  ⚠  1~{len(options)} 사이의 숫자를 입력하세요.")


def get_int_input(prompt: str, min_val: int, max_val: int) -> int:
    """범위 내 정수를 입력받는다."""
    while True:
        raw = input(prompt).strip()
        if raw.isdigit() or (raw.startswith("-") and raw[1:].isdigit()):
            val = int(raw)
            if min_val <= val <= max_val:
                return val
        print(f"  ⚠  {min_val}~{max_val} 사이의 숫자를 입력하세요.")


def get_positive_int(prompt: str) -> int:
    """양의 정수를 입력받는다 (상한 없음)."""
    while True:
        raw = input(prompt).strip()
        if raw.isdigit() and int(raw) > 0:
            return int(raw)
        print("  ⚠  양의 정수를 입력하세요.")


# ─── 결과 출력 ────────────────────────────────────────────────────────────────

def print_period_result(product_name: str, usage_days: int, result: dict) -> None:
    week_num = result.get("주차", (usage_days - 1) // 7 + 1)
    print()
    divider("=")
    print("  📋 환불 계산 결과")
    divider("=")
    print(f"  상품명   : {product_name}")
    if "상품금액" in result:
        print(f"  상품금액 : {result['상품금액']:,}원")
    print(f"  사용일수 : {usage_days}일 ({week_num}주차)")
    divider()
    if result["환불가능"]:
        print(f"  ✅ 환불 가능")
        print(f"  환불금액 : {result['환불금액']:,}원")
    else:
        print("  ❌ 환불 불가 (0원)")
    print(f"  사유     : {result['사유']}")
    divider("=")


def print_time_result(product_name: str, usage_hours: int, result: dict) -> None:
    print()
    divider("=")
    print("  📋 환불 계산 결과")
    divider("=")
    print(f"  상품명   : {product_name}")
    if "상품금액" in result:
        print(f"  상품금액 : {result['상품금액']:,}원")
    print(f"  이용시간 : {usage_hours}시간")
    deduction = usage_hours * 1500
    print(f"  차감금액 : {deduction:,}원  (시간당 1,500원)")
    divider()
    if result["환불가능"]:
        print("  ✅ 환불 가능")
        print(f"  환불금액 : {result['환불금액']:,}원")
    else:
        print("  ❌ 환불 불가 (0원)")
    print(f"  사유     : {result['사유']}")
    divider("=")


def print_extended_result(total_weeks: int, price: int, usage_days: int, result: dict) -> None:
    week_num = result.get("주차", (usage_days - 1) // 7 + 1)
    print()
    divider("=")
    print(f"  📋 확장 환불 계산 결과  ({total_weeks}주권)")
    divider("=")
    print(f"  상품금액 : {price:,}원")
    print(f"  사용일수 : {usage_days}일 ({week_num}주차)")
    print(f"  적용분기 : {result['분기']}")
    print(f"  환불비율 : {result['환불비율']}")
    divider()
    if result["환불가능"]:
        print("  ✅ 환불 가능")
        print(f"  환불금액 : {result['환불금액']:,}원")
    else:
        print("  ❌ 환불 불가 (0원)")
    print(f"  사유     : {result['사유']}")
    divider("=")


# ─── 메뉴 흐름 ────────────────────────────────────────────────────────────────

def run_period_pass() -> None:
    """기간권 환불 계산 흐름."""
    period_products = list(PERIOD_PASS_REFUND_TABLE.keys())
    p_choice = select_from_menu("기간권 종류를 선택하세요:", period_products)
    product_name = period_products[p_choice - 1]

    info = PERIOD_PASS_REFUND_TABLE[product_name]
    max_days = info["total_weeks"] * 7

    print(f"\n  상품금액: {info['price']:,}원 | 이용 가능 기간: 최대 {max_days}일")
    usage_days = get_int_input(f"  사용일수를 입력하세요 (1~{max_days}): ", 1, max_days)

    result = calculate_refund("기간권", product_name, usage_days)
    print_period_result(product_name, usage_days, result)


def run_time_pass() -> None:
    """시간권 환불 계산 흐름."""
    time_products = list(TIME_PASS_PRICES.keys())
    p_choice = select_from_menu("시간권 종류를 선택하세요:", time_products)
    product_name = time_products[p_choice - 1]

    price = TIME_PASS_PRICES[product_name]
    # 이용시간 상한: 상품금액을 시간당 차감액으로 나눈 값 + 여유분
    max_hours = price // 1500 + 50

    print(f"\n  상품금액: {price:,}원 | 시간당 차감: 1,500원 | 환불기한: 구매 후 {TIME_PASS_EXPIRY_DAYS}일")
    usage_hours = get_int_input(f"  이용시간을 입력하세요 (0~{max_hours}시간): ", 0, max_hours)
    days_since = get_int_input(
        f"  구매 후 경과 일수를 입력하세요 (0~365일, 28일 초과 시 환불 불가): ", 0, 365
    )

    result = calculate_refund("시간권", product_name, usage_hours, days_since_purchase=days_since)
    print_time_result(product_name, usage_hours, result)


def run_extended_period() -> None:
    """확장 기간권 환불 계산 흐름 (2~20주권 범용)."""
    print("\n  📊 확장 기간권 환불 계산 (70% / 40% / 20% / 0% 분기 방식)")
    print("  전체 기간을 4분기로 균등 분할하여 환불비율을 적용합니다.\n")

    total_weeks = get_int_input("  주권 기간을 입력하세요 (2~20주): ", 2, 20)
    price = get_positive_int("  상품금액을 입력하세요 (원): ")
    max_days = total_weeks * 7
    usage_days = get_int_input(f"  사용일수를 입력하세요 (1~{max_days}): ", 1, max_days)

    result = calculate_extended_period_refund(total_weeks, price, usage_days)
    print_extended_result(total_weeks, price, usage_days, result)


def main() -> None:
    print()
    print("=" * 44)
    print("     앤딩 스터디카페 환불 계산기")
    print("=" * 44)

    while True:
        mode_options = [
            "표준 상품 환불 계산",
            "확장 기간권 환불 계산 (2~20주권)",
            "종료",
        ]
        mode = select_from_menu("메뉴를 선택하세요:", mode_options)

        if mode == 1:
            # 표준 상품 환불
            product_type_options = [
                "기간권",
                "시간권",
                "당일권 (환불 불가)",
                "스터디룸 (환불 불가, 일정 변경 가능)",
            ]
            pt_choice = select_from_menu("상품 종류를 선택하세요:", product_type_options)

            if pt_choice == 1:
                run_period_pass()
            elif pt_choice == 2:
                run_time_pass()
            elif pt_choice == 3:
                print("\n  ⚠️  당일권은 환불이 불가합니다.")
            else:
                print("\n  ⚠️  스터디룸은 환불이 불가합니다. 예약 일정 변경만 가능합니다.")

        elif mode == 2:
            run_extended_period()

        else:
            print("\n  이용해 주셔서 감사합니다.\n")
            break

        input("\n  계속하려면 Enter를 누르세요...")


if __name__ == "__main__":
    main()
