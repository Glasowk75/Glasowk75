"""
9월 1일-15일 트레이딩 분석
사용자의 관점으로 매매 기회 찾기
"""

import csv
from datetime import datetime

def analyze_september_trading(csv_path):
    """9월 1-15일 데이터 분석"""

    # CSV 읽기
    data = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 9월 1-15일 데이터만
            if '2025-09-0' in row['time'] or '2025-09-1' in row['time']:
                time_str = row['time']
                if '2025-09-01' <= time_str <= '2025-09-15T23':
                    data.append(row)

    print(f"📊 9월 1-15일 데이터: {len(data)}개 봉 ({len(data)/24:.1f}일)")
    print("="*120)

    # 매매 기회 찾기
    opportunities = []

    for i, row in enumerate(data):
        if i < 10:  # 초반 10봉은 스킵
            continue

        try:
            close = float(row['close'])
            rsi = float(row[' rsi'])
            rsi2 = float(row[' rsi2 '])
            adx = float(row['ADX'])
            sma200 = float(row['SMA 200'])
            sma60 = float(row['SMA 60'])
            sma20 = float(row['SMA 20'])
            atr = float(row['ATR'])
            volume = float(row['Volume'])
            volume_ma = float(row['Volume MA'])
            divergence = float(row['Divergence'])
            macd = float(row['MACD'])
            signal = float(row['Signal'])
            high_overlap = int(row['Closest_High_Overlap'])
            low_overlap = int(row['Closest_Low_Overlap'])
            market_struct = int(row['Market_Struct'])
            bos_count = int(row['BOS_Count'])

            # SMA60 대비 가격 위치
            dist_sma60 = (close - sma60) / sma60 * 100

            # 볼륨 배수
            volume_mult = volume / volume_ma if volume_ma > 0 else 0

            # IT 피봇
            it_high = row['IT_High'].strip() if row['IT_High'] else ''
            it_low = row['IT_Low'].strip() if row['IT_Low'] else ''

            # 매매 신호 체크
            signal_type = None
            reason = []

            # === LONG 신호 ===
            if rsi2 >= 52:  # RED LINE - LONG 관점
                # 1. 다이버전스 매수 (강력)
                if divergence == 1 and it_low:
                    signal_type = 'LONG'
                    reason.append(f'상승 다이버전스 (IT Low 피봇)')
                    if low_overlap >= 2:
                        reason.append(f'지지 겹침 {low_overlap}개 (강력)')

                # 2. 과매도 + 고볼륨 반등
                elif rsi < 30 and volume_mult >= 3.0 and dist_sma60 > -2:
                    signal_type = 'LONG'
                    reason.append(f'RSI 과매도 {rsi:.1f}')
                    reason.append(f'고볼륨 {volume_mult:.1f}x')

                # 3. SMA60 지지 + 피봇 겹침
                elif abs(dist_sma60) < 0.5 and low_overlap >= 3:
                    signal_type = 'LONG'
                    reason.append(f'SMA60 근처 (거리 {dist_sma60:.2f}%)')
                    reason.append(f'지지 겹침 {low_overlap}개')

            # === SHORT 신호 ===
            elif rsi2 <= 48:  # YELLOW LINE - SHORT 관점
                # 1. 다이버전스 매도 (강력)
                if divergence == -1 and it_high:
                    signal_type = 'SHORT'
                    reason.append(f'하락 다이버전스 (IT High 피봇)')
                    if high_overlap >= 2:
                        reason.append(f'저항 겹침 {high_overlap}개 (강력)')

                # 2. 과매수 + 고볼륨 하락
                elif rsi > 70 and volume_mult >= 3.0 and dist_sma60 < 2:
                    signal_type = 'SHORT'
                    reason.append(f'RSI 과매수 {rsi:.1f}')
                    reason.append(f'고볼륨 {volume_mult:.1f}x')

                # 3. SMA60 저항 + 피봇 겹침
                elif abs(dist_sma60) < 0.5 and high_overlap >= 3:
                    signal_type = 'SHORT'
                    reason.append(f'SMA60 근처 (거리 {dist_sma60:.2f}%)')
                    reason.append(f'저항 겹침 {high_overlap}개')

            # === 중립 구간 예외 (48 < RSI2 < 52) ===
            else:
                # 강한 다이버전스는 RSI2 필터 무시 가능
                if divergence == 1 and it_low and low_overlap >= 3:
                    signal_type = 'LONG'
                    reason.append(f'⚠️ 중립구간이지만 강력한 상승 다이버전스')
                    reason.append(f'지지 겹침 {low_overlap}개')
                elif divergence == -1 and it_high and high_overlap >= 3:
                    signal_type = 'SHORT'
                    reason.append(f'⚠️ 중립구간이지만 강력한 하락 다이버전스')
                    reason.append(f'저항 겹침 {high_overlap}개')

            if signal_type:
                opportunities.append({
                    'index': i,
                    'time': row['time'],
                    'signal': signal_type,
                    'price': close,
                    'rsi': rsi,
                    'rsi2': rsi2,
                    'dist_sma60': dist_sma60,
                    'volume_mult': volume_mult,
                    'divergence': divergence,
                    'high_overlap': high_overlap,
                    'low_overlap': low_overlap,
                    'reason': reason
                })

        except (ValueError, KeyError) as e:
            continue

    # 결과 출력
    print(f"\n🎯 발견한 매매 기회: {len(opportunities)}개\n")

    for i, opp in enumerate(opportunities[:20], 1):  # 최대 20개만
        print("="*120)
        print(f"{i}. {opp['signal']} 신호 - {opp['time']}")
        print(f"   가격: {opp['price']:,.1f}")
        print(f"   RSI: {opp['rsi']:.1f} | RSI2: {opp['rsi2']:.1f} | SMA60 거리: {opp['dist_sma60']:+.2f}%")
        print(f"   볼륨: {opp['volume_mult']:.1f}x | 다이버전스: {opp['divergence']}")
        print(f"   피봇 겹침: High {opp['high_overlap']}개 / Low {opp['low_overlap']}개")
        print(f"   📌 이유:")
        for r in opp['reason']:
            print(f"      - {r}")

    if len(opportunities) > 20:
        print(f"\n... 외 {len(opportunities) - 20}개 기회 더 있음")

    print("\n" + "="*120)

    # 신호별 통계
    long_count = sum(1 for o in opportunities if o['signal'] == 'LONG')
    short_count = sum(1 for o in opportunities if o['signal'] == 'SHORT')

    print(f"\n📊 신호 통계:")
    print(f"   LONG: {long_count}개")
    print(f"   SHORT: {short_count}개")

    return opportunities

if __name__ == "__main__":
    csv_file = 'BITGET_BTCUSDT.P, 60_7fbcf_with_overlap.csv'

    print("🚀 9월 1-15일 트레이딩 분석 시작\n")

    opportunities = analyze_september_trading(csv_file)

    print(f"\n\n✅ 분석 완료!")
