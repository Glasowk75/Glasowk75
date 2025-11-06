# 📚 Trading AI System - 완전 가이드

## 🎯 프로젝트 개요
- **폴더**: C:\Users\bgs32\trading_ai
- **목적**: 과거 차트 데이터에서 패턴을 자동 발견하고 승률 높은 전략을 생성
- **개발자**: Ban geun
- **협력**: Claude
- **시작일**: 2024-11-06
- **현재 버전**: 1.0

---

## 📁 파일 구조 및 역할

### 1️⃣ pattern_learning_system.py
**역할**: 패턴 자동 발견 및 학습 엔진

**주요 기능**:
- CSV 파일에서 가격 데이터 읽기
- RSI, ADX, SMA 등 지표 계산
- 패턴 조합 자동 테스트 (1개, 2개, 3개 지표 조합)
- 승률 및 수익률 계산
- 신뢰도 점수 산출
- Pine Script 자동 생성
- 데이터베이스 저장

**실행 방법**:
```bash
python pattern_learning_system.py                 # 기본 BTC 파일 처리
python pattern_learning_system.py mydata.csv      # 특정 파일 처리
```

### 2️⃣ trading_ai_server.py
**역할**: REST API 서버 (패턴 조회 및 분석)

**엔드포인트**:
- GET  /           - 메인 페이지
- GET  /status     - 시스템 상태
- GET  /patterns   - 패턴 목록
- POST /analyze    - 데이터 분석
- GET  /stats      - 통계 정보
- GET  /docs       - API 문서 (Swagger UI)

**실행**: 
```bash
python trading_ai_server.py
# 접속: http://localhost:8000
```

### 3️⃣ trading_knowledge.db
**역할**: SQLite 데이터베이스 (모든 학습 결과 저장)

**테이블 구조**:
- patterns: 발견된 패턴 정보
  - pattern_name (패턴명)
  - conditions (조건 JSON)
  - win_rate_10 (10캔들 승률)
  - avg_return_10 (평균 수익률)
  - confidence_score (신뢰도)
  - sample_size (샘플 수)

### 4️⃣ auto_strategy.pine
**역할**: TradingView용 자동 생성 전략

**사용법**:
1. TradingView 차트 열기
2. Pine Editor 열기
3. 코드 복사/붙여넣기
4. "Add to Chart" 클릭

### 5️⃣ discovered_patterns.json
**역할**: 패턴 백업 및 상세 정보 (JSON 형식)

---

## 📊 현재 시스템 상태

### 발견된 주요 패턴

| 순위 | 패턴명 | 조건 | 승률 | 신뢰도 |
|------|--------|------|------|--------|
| 1 | RSI70_SMA1 | RSI>70 & SMA거리<1% | 79.4% | 72.6 |
| 2 | RSI30_ADX40 | RSI<30 & ADX>40 | 67.8% | 67.4 |
| 3 | Pivot_Support_RSI | 피봇지지 & RSI<35 | 65.0% | 58.7 |
| 4 | RSI25_ADX40 | RSI<25 & ADX>40 | 66.7% | 56.6 |
| 5 | RSI35_ADX40 | RSI<35 & ADX>40 | 64.8% | 56.3 |
| 6 | RSI30_SMA1 | RSI<30 & SMA거리<1% | 55.6% | 53.3 |
| 7 | RSI20_ADX40 | RSI<20 & ADX>40 | 60.0% | 52.0 |

### 백테스트 결과 (TradingView)
- 기간: 2년 반
- 수익률: -32.44% (개선 필요)
- 거래 횟수: 492회
- 승률: 53.46%

---

## 🚀 빠른 시작 가이드

### 1. 시스템 확인
```powershell
cd C:\Users\bgs32\trading_ai
dir
```

### 2. 패턴 학습
```powershell
python pattern_learning_system.py
```

### 3. 서버 시작
```powershell
python trading_ai_server.py
```

### 4. 브라우저 확인
http://localhost:8000

---

## 🔧 개선 필요 사항

### 단기 (즉시 가능)
1. **패턴 필터링 강화**
   - 승률 기준을 60% → 70%로 상향
   - 신뢰도 50 → 60으로 상향

2. **손익비 조정**
   - 익절: 2% → 1%
   - 손절: 1% → 0.5%

### 중기 (1-2주)
1. **추가 지표 통합**
   - Volume 분석
   - Bollinger Bands
   - MACD 다이버전스

2. **다중 시간대 분석**
   - 5분, 15분, 4시간 데이터 추가
   - 멀티타임프레임 확인

### 장기 (1개월+)
1. **머신러닝 통합**
   - Random Forest
   - XGBoost
   - LSTM

2. **실시간 자동매매**
   - Exchange API 연동
   - 리스크 관리 시스템

---

## 💡 일일 운영 가이드

### 아침 루틴
1. 서버 상태 확인: http://localhost:8000/status
2. 새 데이터 다운로드
3. 패턴 재학습: `python pattern_learning_system.py`
4. Pine Script 업데이트

### 저녁 리뷰
1. 당일 성과 확인
2. 실패 패턴 분석
3. 파라미터 조정
4. 백업: `copy *.db backup\`

---

## 🆘 문제 해결

### DB 오류
```powershell
del trading_knowledge.db
python pattern_learning_system.py
```

### 서버 포트 충돌
```powershell
# trading_ai_server.py 마지막 줄 수정
# port=8000 → port=8001
```

### 패키지 오류
```powershell
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn pandas numpy
```

---

## 📝 새 대화창 시작 템플릿
```
안녕 Claude, Trading AI 시스템 이어서 개발하자.

폴더: C:\Users\bgs32\trading_ai
현재 상태:
- 패턴 7개 발견 (최고: RSI70_SMA1 79.4%)
- 서버: localhost:8000
- 백테스트: -32.44% (개선 필요)

오늘 목표: [선택]
1. 백테스트 성과 개선
2. 새 데이터로 학습 확장
3. 실시간 알림 구현
4. 리스크 관리 강화

파일들 살펴보고 시작해줘.
```

---

## 📞 연락 & 지원

개발자: Ban geun
협력 AI: Claude (Anthropic)
프로젝트 시작: 2024-11-06
최종 업데이트: 2024-11-06

---

*이 문서는 새로운 개발 세션을 시작할 때 참고하세요.*
*시스템이 업데이트되면 이 문서도 함께 업데이트하세요.*
