# 앤딩 스터디카페 환불 계산기

## 배포
- Streamlit Cloud URL: (배포 링크 기입)
- GitHub 저장소: (저장소 URL 기입)

## 프로젝트 맥락
- 무인화연구소 환불 시스템
- 로컬 실행: `streamlit run app.py`
- CLI 실행: `python main.py`
- 테스트: `python test_refund.py`

## 파일 구조
- `refund_calculator.py` — 핵심 계산 로직 (공개 API)
- `main.py` — CLI 대화형 인터페이스
- `app.py` — Streamlit 웹 UI (탭 4개)
- `test_refund.py` — 단위 테스트 46개

## 환경
- Python 3.14
- 가상환경: `.venv/`
- 의존성: streamlit, pillow 등 (.venv에 설치됨)

## 작업 히스토리
- 환불 계산기 로직 완성 (refund_calculator.py)
- Streamlit 웹 UI 완성 (app.py) — 탭: 기간권 / 시간권 / 확장기간권 / 환불규정
- 단위 테스트 46개 작성 (test_refund.py)
- CLAUDE.md 추가 — 다른 컴퓨터에서도 컨텍스트 유지 목적
