# 앤딩 스터디카페 환불 계산기

## 배포
- Streamlit Cloud URL: https://muinlab-refund.streamlit.app/
- GitHub 저장소: https://github.com/kdb9325/study-cafe-refund

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

## 멀티 PC 작업 규칙

### 기본 흐름
```
작업 시작     →  git pull
중간 저장     →  git add . && git commit -m "WIP: 작업내용"
작업 종료     →  git push
자리 뜨기 전  →  git push (필수)
```

### 급하게 자리 뜰 때 (미완성 작업)
```bash
git stash        # 미완성 작업 임시 저장
git push         # stash 상태 원격에 반영

# 다른 PC에서 이어받기
git pull
git stash pop    # 임시 저장 복원
```

### 핵심 원칙
> 로컬에만 있는 건 없는 것과 같다 — 작업 후 반드시 push

---

## 작업 히스토리
- 환불 계산기 로직 완성 (refund_calculator.py)
- Streamlit 웹 UI 완성 (app.py) — 탭: 기간권 / 시간권 / 확장기간권 / 환불규정
- 단위 테스트 46개 작성 (test_refund.py)
- CLAUDE.md 추가 — 다른 컴퓨터에서도 컨텍스트 유지 목적
