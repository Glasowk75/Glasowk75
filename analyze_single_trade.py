"""
단일 거래 상세 분석
9월 8일 상승 다이버전스 LONG 거래
"""

import csv
from datetime import datetime

def analyze_single_trade():
    """9월 8일 상승 다이버전스 LONG 거래 분석"""

    csv_file = 'BITGET_BTCUSDT.P, 60_7fbcf_with_overlap.csv'

    # CSV 읽기
    data = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if '2025-09-07' in row['time'] or '2025-09-08' in row['time'] or '2025-09-09' in row['time']:
                data.append(row)

    print("="*120)
    print("📈 거래 #1: LONG - 9월 8일 상승 다이버전스")
    print("="*120)

    # 진입 시점 찾기: 9월 8일 16:00
    entry_index = None
    for i, row in enumerate(data):
        if row['time'] == '2025-09-08T16:00:00+09:00':
            entry_index = i
            break

    if entry_index is None:
        print("❌ 진입 시점을 찾을 수 없습니다.")
        return

    entry_row = data[entry_index]
    entry_price = float(entry_row['close'])

    print("\n🎯 진입 분석")
    print("-" * 120)
    print(f"📅 진입 시각: 2025-09-08 16:00")
    print(f"💰 진입 가격: {entry_price:,.1f}")
    print()

    # 진입 전 3시간 상황
    print("📊 진입 전 상황 (3시간 전부터):")
    print("-" * 120)
    for i in range(max(0, entry_index-3), entry_index+1):
        row = data[i]
        time = row['time'].split('T')[1][:5]
        close = float(row['close'])
        rsi = float(row[' rsi'])
        rsi2 = float(row[' rsi2 '])
        divergence = float(row['Divergence'])
        volume = float(row['Volume'])
        volume_ma = float(row['Volume MA'])
        volume_mult = volume / volume_ma if volume_ma > 0 else 0
        it_low = row['IT_Low'].strip() if row['IT_Low'] else ''
        low_overlap = int(row['Closest_Low_Overlap'])

        marker = "👉 [진입]" if i == entry_index else ""
        div_marker = "🔴 다이버전스!" if divergence != 0 else ""

        print(f"{time}  가격: {close:>9,.1f}  RSI: {rsi:>5.1f}  RSI2: {rsi2:>5.1f}  "
              f"볼륨: {volume_mult:>4.1f}x  IT Low: {it_low:>10}  겹침: {low_overlap}개  "
              f"{div_marker} {marker}")

    print()
    print("✅ 진입 근거:")
    print(f"   1. 상승 다이버전스 발생 (IT Low 피봇)")
    print(f"   2. 고볼륨 진입: {float(entry_row['Volume']) / float(entry_row['Volume MA']):.1f}x")
    print(f"   3. RSI2: {float(entry_row[' rsi2 ']):.1f} (중립구간이지만 강력한 다이버전스)")
    print(f"   4. 지지 피봇 겹침: {entry_row['Closest_Low_Overlap']}개")
    print()

    # 진입 후 가격 변화 추적 (익절/손절 조건 확인)
    print("\n📈 진입 후 가격 변화")
    print("-" * 120)
    print("익절 조건 체크:")
    print("  - RSI 과열 (>70)")
    print("  - RSI/RSI2 크로스")
    print("  - MACD 크로스")
    print("  - ADX 과열 (>70)")
    print("  - ATR2 이상 상승 후 저항")
    print()
    print("손절 조건: ATR2 이하 하락 (진입가 대비 -1.5% 이상)")
    print("-" * 120)

    entry_rsi2 = float(entry_row[' rsi2 '])
    entry_macd = float(entry_row['MACD'])
    entry_signal = float(entry_row['Signal'])
    atr2_percent = float(entry_row['ATR2'])

    exit_found = False
    exit_type = None
    exit_index = None

    for i in range(entry_index + 1, min(entry_index + 25, len(data))):  # 최대 24시간 추적
        row = data[i]
        time = row['time']
        close = float(row['close'])
        high = float(row['high'])
        low = float(row['low'])
        rsi = float(row[' rsi'])
        rsi2 = float(row[' rsi2 '])
        macd = float(row['MACD'])
        signal = float(row['Signal'])
        adx = float(row['ADX'])

        pnl_percent = (close - entry_price) / entry_price * 100
        max_gain = (high - entry_price) / entry_price * 100
        max_loss = (low - entry_price) / entry_price * 100

        time_display = time.split('T')[1][:5]

        # 익절/손절 조건 체크
        exit_reason = []

        # RSI 과열
        if rsi > 70:
            exit_reason.append(f"RSI 과열 {rsi:.1f}")

        # RSI/RSI2 크로스 (하락 전환)
        if rsi < rsi2 and float(data[i-1][' rsi']) > float(data[i-1][' rsi2 ']):
            exit_reason.append("RSI/RSI2 데드크로스")

        # MACD 크로스 (하락 전환)
        prev_macd = float(data[i-1]['MACD'])
        prev_signal = float(data[i-1]['Signal'])
        if macd < signal and prev_macd > prev_signal:
            exit_reason.append("MACD 데드크로스")

        # ADX 과열
        if adx > 70:
            exit_reason.append(f"ADX 과열 {adx:.1f}")

        # 충분한 수익 + 저항
        high_overlap = int(row['Closest_High_Overlap'])
        if pnl_percent > atr2_percent and high_overlap >= 3:
            exit_reason.append(f"ATR2 이상 상승({pnl_percent:.2f}%) + 저항 {high_overlap}개")

        # 손절
        if pnl_percent < -1.5:
            exit_reason.append(f"손절 {pnl_percent:.2f}%")
            exit_type = "손절"
            exit_found = True
            exit_index = i

        # 익절 조건이 2개 이상이면 익절
        if len(exit_reason) >= 2 and pnl_percent > 0:
            exit_type = "익절"
            exit_found = True
            exit_index = i

        status = "🟢" if pnl_percent > 0 else "🔴"
        exit_marker = f"👈 [{exit_type}]" if exit_found and exit_index == i else ""

        print(f"{time_display}  {close:>9,.1f}  손익: {status} {pnl_percent:>+6.2f}%  "
              f"최고: {max_gain:>+6.2f}%  최저: {max_loss:>+6.2f}%  "
              f"RSI: {rsi:>5.1f}  RSI2: {rsi2:>5.1f}  ADX: {adx:>5.1f}")

        if exit_reason:
            print(f"      ⚠️  {', '.join(exit_reason)}  {exit_marker}")

        if exit_found and exit_index == i:
            print()
            print("="*120)
            print(f"🏁 청산 결정: {exit_type}")
            print("="*120)
            print(f"청산 가격: {close:,.1f}")
            print(f"손익: {pnl_percent:+.2f}%")
            print(f"청산 근거: {', '.join(exit_reason)}")
            break

    if not exit_found:
        print()
        print("⚠️  24시간 내에 명확한 청산 신호를 찾지 못했습니다.")
        print("    실제로는 어떻게 청산하셨나요?")

if __name__ == "__main__":
    analyze_single_trade()
