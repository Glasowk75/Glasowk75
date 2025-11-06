"""
다이버전스 계산기
Pine Script 로직을 Python으로 구현
"""

import csv

def calculate_divergence(csv_path):
    """CSV 파일에서 다이버전스 계산"""

    # CSV 읽기
    data = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        for row in reader:
            data.append(row)

    # 다이버전스 컬럼 추가
    for row in data:
        row['Divergence'] = 0.0
        row['Div_Type'] = ''

    # IT 피봇 고점 배열 만들기
    it_high_pivots = []
    for idx, row in enumerate(data):
        if row['IT_High'] and row['IT_High'] != 'NaN':
            try:
                it_high_pivots.append({
                    'barIndex': idx,
                    'price': float(row['IT_High']),
                    'rsiValue': float(row['  rsi']),
                    'close': float(row['close']),
                    'atr': float(row['ATR'])
                })
            except (ValueError, KeyError):
                pass

    # IT 피봇 저점 배열 만들기
    it_low_pivots = []
    for idx, row in enumerate(data):
        if row['IT_Low'] and row['IT_Low'] != 'NaN':
            try:
                it_low_pivots.append({
                    'barIndex': idx,
                    'price': float(row['IT_Low']),
                    'rsiValue': float(row['  rsi']),
                    'close': float(row['close']),
                    'atr': float(row['ATR'])
                })
            except (ValueError, KeyError):
                pass

    print(f"📊 IT 피봇 고점: {len(it_high_pivots)}개")
    print(f"📊 IT 피봇 저점: {len(it_low_pivots)}개")

    # 하락 다이버전스 체크 (IT 고점 기반)
    for i in range(len(it_high_pivots)):
        if i < 2:  # 최소 2개 이상 필요
            continue

        curr = it_high_pivots[i]

        # 이전 2-3개 피봇과 비교
        for lookback in [2, 3]:
            if i < lookback:
                continue

            prev = it_high_pivots[i - lookback]

            price_higher = curr['price'] > prev['price']
            rsi_lower = curr['rsiValue'] < prev['rsiValue']
            price_change = abs(curr['price'] - prev['price']) / curr['close'] * 100

            # Regular Bearish Divergence: 가격 상승 + RSI 하락
            if rsi_lower and price_higher and price_change < curr['atr'] * 1.0:
                data[curr['barIndex']]['Divergence'] = -1
                data[curr['barIndex']]['Div_Type'] = f'Bearish (고점 {lookback}봉 전)'
                break

    # 상승 다이버전스 체크 (IT 저점 기반)
    for i in range(len(it_low_pivots)):
        if i < 2:
            continue

        curr = it_low_pivots[i]

        # 이전 2-3개 피봇과 비교
        for lookback in [2, 3]:
            if i < lookback:
                continue

            prev = it_low_pivots[i - lookback]

            price_lower = curr['price'] < prev['price']
            rsi_higher = curr['rsiValue'] > prev['rsiValue']

            # Regular Bullish Divergence: 가격 하락 + RSI 상승
            if rsi_higher and price_lower:
                data[curr['barIndex']]['Divergence'] = 1
                data[curr['barIndex']]['Div_Type'] = f'Bullish (저점 {lookback}봉 전)'
                break

    # 통계
    bullish_count = sum(1 for row in data if row['Divergence'] == 1)
    bearish_count = sum(1 for row in data if row['Divergence'] == -1)

    print(f"\n✅ 다이버전스 계산 완료!")
    print(f"   상승 다이버전스: {bullish_count}개")
    print(f"   하락 다이버전스: {bearish_count}개")

    # 저장
    output_path = csv_path.replace('.csv', '_with_divergence.csv')
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(headers) + ['Divergence', 'Div_Type'])
        writer.writeheader()
        writer.writerows(data)

    print(f"\n💾 저장 완료: {output_path}")

    return data, output_path

def show_divergence_examples(data, num_examples=5):
    """다이버전스 예시 출력"""

    print("\n" + "="*120)
    print("📌 상승 다이버전스 예시")
    print("="*120)

    bullish = [row for row in data if row['Divergence'] == 1][:num_examples]
    for row in bullish:
        print(f"\n⏰ {row['time']}")
        print(f"   가격: {float(row['close']):.1f} | RSI: {float(row['  rsi']):.2f}")
        print(f"   타입: {row['Div_Type']}")

    print("\n" + "="*120)
    print("📌 하락 다이버전스 예시")
    print("="*120)

    bearish = [row for row in data if row['Divergence'] == -1][:num_examples]
    for row in bearish:
        print(f"\n⏰ {row['time']}")
        print(f"   가격: {float(row['close']):.1f} | RSI: {float(row['  rsi']):.2f}")
        print(f"   타입: {row['Div_Type']}")

if __name__ == "__main__":
    csv_file = 'BITGET_BTCUSDT.P, 60_552b6.csv'

    print("🚀 다이버전스 계산 시작...\n")

    data, output_file = calculate_divergence(csv_file)
    show_divergence_examples(data, num_examples=10)

    print(f"\n\n✅ 완료! 새 파일을 사용하세요: {output_file}")
