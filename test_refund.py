"""
앤딩 스터디카페 환불 계산기 - 단위 테스트

실행 방법:
  python test_refund.py          # 직접 실행
  python -m pytest test_refund.py -v  # pytest 사용 시
"""
import unittest
from refund_calculator import calculate_refund, calculate_extended_period_refund


# ─── 기간권 테스트 ────────────────────────────────────────────────────────────

class TestPeriodPassRefund(unittest.TestCase):
    """기간권 환불 계산 테스트 (고정 금액 브라켓 방식)"""

    # ── 필수 테스트 케이스 ─────────────────────────────────────────────────

    def test_open_4week_22days_no_refund(self):
        """오픈행사 4주권 22일 사용 → 0원 (4주차 이후, 환불 불가)"""
        result = calculate_refund("기간권", "오픈행사 4주권", 22)
        self.assertEqual(result["환불금액"], 0)
        self.assertFalse(result["환불가능"])
        self.assertEqual(result["주차"], 4)

    def test_open_4week_9days(self):
        """오픈행사 4주권 9일 사용 → 31,600원 (2주차, 8~14일)"""
        result = calculate_refund("기간권", "오픈행사 4주권", 9)
        self.assertEqual(result["환불금액"], 31_600)
        self.assertTrue(result["환불가능"])
        self.assertEqual(result["주차"], 2)

    def test_4week_7days(self):
        """4주권 7일 사용 → 76,300원 (1주차, 1~7일 마지막 날)"""
        result = calculate_refund("기간권", "4주권", 7)
        self.assertEqual(result["환불금액"], 76_300)
        self.assertTrue(result["환불가능"])
        self.assertEqual(result["주차"], 1)

    # ── 2주권 ──────────────────────────────────────────────────────────────

    def test_2week_week1(self):
        """2주권 1주차 (5일) → 22,000원 (결제금액의 40%)"""
        result = calculate_refund("기간권", "2주권", 5)
        self.assertEqual(result["환불금액"], 22_000)
        self.assertTrue(result["환불가능"])

    def test_2week_week1_boundary(self):
        """2주권 1주차 마지막 날 (7일) → 22,000원"""
        result = calculate_refund("기간권", "2주권", 7)
        self.assertEqual(result["환불금액"], 22_000)

    def test_2week_week2_no_refund(self):
        """2주권 2주차 (8일) → 0원 (환불 불가)"""
        result = calculate_refund("기간권", "2주권", 8)
        self.assertEqual(result["환불금액"], 0)
        self.assertFalse(result["환불가능"])

    # ── 4주권 ──────────────────────────────────────────────────────────────

    def test_4week_week1_day1(self):
        """4주권 1일차 → 76,300원 (1주차)"""
        result = calculate_refund("기간권", "4주권", 1)
        self.assertEqual(result["환불금액"], 76_300)

    def test_4week_week2(self):
        """4주권 10일 사용 → 43,600원 (2주차, 8~14일)"""
        result = calculate_refund("기간권", "4주권", 10)
        self.assertEqual(result["환불금액"], 43_600)

    def test_4week_week3(self):
        """4주권 15일 사용 → 21,800원 (3주차, 15~21일)"""
        result = calculate_refund("기간권", "4주권", 15)
        self.assertEqual(result["환불금액"], 21_800)

    def test_4week_week4_no_refund(self):
        """4주권 22일 사용 → 0원 (4주차 이후)"""
        result = calculate_refund("기간권", "4주권", 22)
        self.assertEqual(result["환불금액"], 0)
        self.assertFalse(result["환불가능"])

    # ── 고정석 4주권 ───────────────────────────────────────────────────────

    def test_fixed_4week_week1(self):
        """고정석 4주권 1주차 (3일) → 125,300원"""
        result = calculate_refund("기간권", "고정석 4주권", 3)
        self.assertEqual(result["환불금액"], 125_300)

    def test_fixed_4week_week2(self):
        """고정석 4주권 2주차 → 71,600원"""
        result = calculate_refund("기간권", "고정석 4주권", 10)
        self.assertEqual(result["환불금액"], 71_600)

    def test_fixed_4week_week3(self):
        """고정석 4주권 3주차 → 35,800원"""
        result = calculate_refund("기간권", "고정석 4주권", 20)
        self.assertEqual(result["환불금액"], 35_800)

    # ── 관리고정석 4주권 ───────────────────────────────────────────────────

    def test_managed_fixed_4week_week1(self):
        """관리고정석 4주권 1주차 → 160,300원"""
        result = calculate_refund("기간권", "관리고정석 4주권", 1)
        self.assertEqual(result["환불금액"], 160_300)

    def test_managed_fixed_4week_week2(self):
        """관리고정석 4주권 2주차 (10일) → 91,600원"""
        result = calculate_refund("기간권", "관리고정석 4주권", 10)
        self.assertEqual(result["환불금액"], 91_600)

    def test_managed_fixed_4week_week3(self):
        """관리고정석 4주권 3주차 → 45,800원"""
        result = calculate_refund("기간권", "관리고정석 4주권", 19)
        self.assertEqual(result["환불금액"], 45_800)

    # ── 오픈행사 4주권 ─────────────────────────────────────────────────────

    def test_open_4week_week1(self):
        """오픈행사 4주권 1주차 → 55,300원 (약 70%)"""
        result = calculate_refund("기간권", "오픈행사 4주권", 1)
        self.assertEqual(result["환불금액"], 55_300)

    def test_open_4week_week3(self):
        """오픈행사 4주권 3주차 (21일) → 15,800원 (20%)"""
        result = calculate_refund("기간권", "오픈행사 4주권", 21)
        self.assertEqual(result["환불금액"], 15_800)


# ─── 시간권 테스트 ────────────────────────────────────────────────────────────

class TestTimePassRefund(unittest.TestCase):
    """시간권 환불 계산 테스트 (이용시간 × 1,500원 차감)"""

    # ── 필수 테스트 케이스 ─────────────────────────────────────────────────

    def test_open100_9hours(self):
        """오픈100시간권 9시간 사용 → 55,500원
        계산: 69,000 - (9 × 1,500) = 69,000 - 13,500 = 55,500"""
        result = calculate_refund("시간권", "오픈100시간권", 9)
        self.assertEqual(result["환불금액"], 55_500)
        self.assertTrue(result["환불가능"])

    def test_100hour_zero_usage(self):
        """100시간권 0시간 사용 → 95,000원 (전액 환불)"""
        result = calculate_refund("시간권", "100시간권", 0)
        self.assertEqual(result["환불금액"], 95_000)
        self.assertTrue(result["환불가능"])

    def test_200hour_120hours_no_refund(self):
        """200시간권 120시간 사용 → 0원
        계산: 180,000 - (120 × 1,500) = 180,000 - 180,000 = 0"""
        result = calculate_refund("시간권", "200시간권", 120)
        self.assertEqual(result["환불금액"], 0)
        self.assertFalse(result["환불가능"])

    # ── 추가 케이스 ────────────────────────────────────────────────────────

    def test_200hour_50hours(self):
        """200시간권 50시간 사용 → 105,000원
        계산: 180,000 - (50 × 1,500) = 180,000 - 75,000 = 105,000"""
        result = calculate_refund("시간권", "200시간권", 50)
        self.assertEqual(result["환불금액"], 105_000)

    def test_100hour_63hours(self):
        """100시간권 63시간 사용 → 500원 (소액 환불)
        계산: 95,000 - (63 × 1,500) = 95,000 - 94,500 = 500"""
        result = calculate_refund("시간권", "100시간권", 63)
        self.assertEqual(result["환불금액"], 500)
        self.assertTrue(result["환불가능"])

    def test_100hour_64hours_zero(self):
        """100시간권 64시간 사용 → 0원
        계산: 95,000 - (64 × 1,500) = 95,000 - 96,000 = -1,000 → 0"""
        result = calculate_refund("시간권", "100시간권", 64)
        self.assertEqual(result["환불금액"], 0)
        self.assertFalse(result["환불가능"])

    def test_time_pass_within_28days(self):
        """시간권 구매 후 28일 → 정상 환불"""
        result = calculate_refund("시간권", "100시간권", 0, days_since_purchase=28)
        self.assertEqual(result["환불금액"], 95_000)
        self.assertTrue(result["환불가능"])

    def test_time_pass_expired_29days(self):
        """시간권 구매 후 29일 → 환불 불가 (기한 초과)"""
        result = calculate_refund("시간권", "100시간권", 0, days_since_purchase=29)
        self.assertEqual(result["환불금액"], 0)
        self.assertFalse(result["환불가능"])


# ─── 환불 불가 상품 테스트 ───────────────────────────────────────────────────

class TestNonRefundableProducts(unittest.TestCase):
    """환불 불가 상품 테스트"""

    def test_daily_pass(self):
        """당일권 → 환불 불가"""
        result = calculate_refund("당일권", "당일권", 1)
        self.assertEqual(result["환불금액"], 0)
        self.assertFalse(result["환불가능"])

    def test_study_room(self):
        """스터디룸 → 환불 불가"""
        result = calculate_refund("스터디룸", "스터디룸", 1)
        self.assertEqual(result["환불금액"], 0)
        self.assertFalse(result["환불가능"])
        # 스터디룸은 일정 변경 안내 포함
        self.assertIn("변경", result["사유"])


# ─── 확장 기간권 테스트 ──────────────────────────────────────────────────────

class TestExtendedPeriodRefund(unittest.TestCase):
    """확장 기간권 환불 계산 테스트 (70% / 40% / 20% / 0% 분기 방식)"""

    def test_8week_quarter1(self):
        """8주권 1주차 → 1분기(70%) 적용
        계산: 100,000 × 70% = 70,000"""
        result = calculate_extended_period_refund(8, 100_000, 1)
        self.assertEqual(result["환불금액"], 70_000)
        self.assertTrue(result["환불가능"])

    def test_8week_quarter2(self):
        """8주권 3주차 (day 15) → 2분기(40%) 적용
        8주권 quarter_size=2: 주차 3은 2분기 (3 > 2, 3 ≤ 4)
        계산: 100,000 × 40% = 40,000"""
        result = calculate_extended_period_refund(8, 100_000, 15)
        self.assertEqual(result["환불금액"], 40_000)

    def test_8week_quarter3(self):
        """8주권 5주차 (day 29) → 3분기(20%) 적용
        계산: 100,000 × 20% = 20,000"""
        result = calculate_extended_period_refund(8, 100_000, 29)
        self.assertEqual(result["환불금액"], 20_000)

    def test_8week_quarter4_no_refund(self):
        """8주권 7주차 (day 43) → 4분기(0%), 환불 불가"""
        result = calculate_extended_period_refund(8, 100_000, 43)
        self.assertEqual(result["환불금액"], 0)
        self.assertFalse(result["환불가능"])

    def test_12week_last_quarter(self):
        """12주권 4분기 (day 65, week 10) → 0%, 환불 불가
        quarter_size=3: week 10은 (10-1)/3=3.0 → quarter_idx=3 → 0%"""
        result = calculate_extended_period_refund(12, 200_000, 65)
        self.assertEqual(result["환불금액"], 0)
        self.assertFalse(result["환불가능"])

    def test_12week_quarter1(self):
        """12주권 1주차 → 70% 적용
        계산: 200,000 × 70% = 140,000"""
        result = calculate_extended_period_refund(12, 200_000, 1)
        self.assertEqual(result["환불금액"], 140_000)

    def test_rounding_100won(self):
        """환불금액 100원 단위 반올림 확인
        150,000 × 70% = 105,000 → 정확히 100원 단위"""
        result = calculate_extended_period_refund(4, 150_000, 1)
        self.assertEqual(result["환불금액"], 105_000)
        self.assertEqual(result["환불금액"] % 100, 0)

    def test_result_contains_quarter_info(self):
        """결과 딕셔너리에 분기 정보 포함 여부 확인"""
        result = calculate_extended_period_refund(8, 100_000, 1)
        self.assertIn("분기", result)
        self.assertIn("환불비율", result)
        self.assertIn("주차", result)


# ─── 입력값 검증 테스트 ──────────────────────────────────────────────────────

class TestInputValidation(unittest.TestCase):
    """잘못된 입력에 대한 예외 처리 테스트"""

    def test_invalid_product_type(self):
        """알 수 없는 상품 종류 → ValueError"""
        with self.assertRaises(ValueError):
            calculate_refund("기타상품", "4주권", 5)

    def test_invalid_period_product_name(self):
        """알 수 없는 기간권 상품명 → ValueError"""
        with self.assertRaises(ValueError):
            calculate_refund("기간권", "없는상품", 5)

    def test_invalid_time_product_name(self):
        """알 수 없는 시간권 상품명 → ValueError"""
        with self.assertRaises(ValueError):
            calculate_refund("시간권", "없는시간권", 5)

    def test_usage_exceeds_period(self):
        """4주권 사용일수 초과 (29일) → ValueError"""
        with self.assertRaises(ValueError):
            calculate_refund("기간권", "4주권", 29)

    def test_usage_zero_period(self):
        """사용일수 0 → ValueError"""
        with self.assertRaises(ValueError):
            calculate_refund("기간권", "4주권", 0)

    def test_negative_usage_hours(self):
        """음수 이용시간 → ValueError"""
        with self.assertRaises(ValueError):
            calculate_refund("시간권", "100시간권", -1)

    def test_extended_invalid_weeks_below(self):
        """확장 기간권: 1주 (범위 미달) → ValueError"""
        with self.assertRaises(ValueError):
            calculate_extended_period_refund(1, 100_000, 1)

    def test_extended_invalid_weeks_above(self):
        """확장 기간권: 21주 (범위 초과) → ValueError"""
        with self.assertRaises(ValueError):
            calculate_extended_period_refund(21, 100_000, 1)

    def test_extended_invalid_price(self):
        """확장 기간권: 상품금액 0 → ValueError"""
        with self.assertRaises(ValueError):
            calculate_extended_period_refund(8, 0, 1)

    def test_extended_usage_exceeds_total(self):
        """확장 기간권: 사용일수가 전체 기간 초과 → ValueError"""
        with self.assertRaises(ValueError):
            calculate_extended_period_refund(4, 100_000, 29)  # 4주 = 28일


if __name__ == "__main__":
    unittest.main(verbosity=2)
