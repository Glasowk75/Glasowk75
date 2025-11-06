# 🚀 트레이딩 AI 시스템 - 빠른 시작

## ✅ 완성된 것들

### 1. **자동 생성된 Pine Script 전략**
- 파일: `auto_strategy.pine`
- 최고 패턴 3개 포함
- **바로 TradingView에 복사해서 사용 가능!**

### 2. **발견된 최고 패턴들**

| 패턴명 | 조건 | 승률 | 평균수익 |
|--------|------|------|----------|
| RSI70_SMA1 | RSI>70 & SMA20 거리<1% | **79.4%** | +0.76% |
| RSI30_ADX40 | RSI<30 & ADX>40 | **67.8%** | +0.53% |
| RSI25_ADX40 | RSI<25 & ADX>40 | **66.7%** | +0.73% |

### 3. **Python 시스템 파일들**
- `pattern_learning_system.py` - 패턴 자동 발견 시스템
- `trading_ai_server.py` - 실시간 웹훅 서버
- `discovered_patterns.json` - 발견된 모든 패턴 데이터

## 📌 바로 사용하기

### Step 1: Pine Script 적용
1. TradingView 차트 열기
2. Pine Editor 열기
3. `auto_strategy.pine` 내용 복사/붙여넣기
4. "Add to Chart" 클릭

### Step 2: Alert 설정 (선택사항)
```json
{
    "symbol": "{{ticker}}",
    "price": {{close}},
    "rsi": {{plot_0}},
    "adx": {{plot_1}},
    "time": "{{time}}"
}
```
Webhook URL: `http://your-server:8000/webhook`

### Step 3: Python 서버 실행 (선택사항)
```bash
# 필요 패키지 설치
pip install fastapi uvicorn pandas sqlite3

# 서버 실행
python trading_ai_server.py
```

## 💡 핵심 인사이트

1. **RSI 과매수(>70)가 오히려 상승 신호!**
   - SMA20 근처에서 RSI>70일 때 79.4% 승률
   - 강한 모멘텀의 지속성을 보여줌

2. **ADX>40에서 RSI 과매도가 효과적**
   - 강한 추세에서의 일시적 조정
   - 추세 방향으로 진입하는 좋은 기회

3. **조합이 핵심**
   - 단일 지표보다 2-3개 조합이 훨씬 효과적
   - 맥락(추세 강도, 이평선 위치)이 중요

## 🔄 지속적 개선

이 시스템은:
- 새로운 데이터로 자동 학습
- 패턴 성과 자동 추적
- Pine Script 자동 업데이트

매일 실행하면서 점점 더 정확해집니다!

---
Created with ❤️ by Ban geun & Claude
