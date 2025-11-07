"""
피봇 겹침 개수 계산기
- IT_High, IT_Low 피봇의 겹침 개수 계산
- ATR × 1.0 범위 내에 있는 피봇 개수 세기
"""

import csv

def calculate_pivot_overlap(csv_path, overlap_range_atr_multiplier=1.0):
    """피봇 겹침 개수 계산"""

    # CSV 읽기
    data = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)

    print(f"📊 CSV 로드: {len(data)}개 봉")

    # IT 피봇 수집
    it_high_pivots = []
    it_low_pivots = []

    for idx, row in enumerate(data):
        # IT_High 피봇
        if row['IT_High'] and row['IT_High'].strip():
            try:
                it_high_pivots.append({
                    'index': idx,
                    'price': float(row['IT_High'].strip()),
                    'time': row['time'],
                    'atr': float(row['ATR'].strip())
                })
            except ValueError:
                pass

        # IT_Low 피봇
        if row['IT_Low'] and row['IT_Low'].strip():
            try:
                it_low_pivots.append({
                    'index': idx,
                    'price': float(row['IT_Low'].strip()),
                    'time': row['time'],
                    'atr': float(row['ATR'].strip())
                })
            except ValueError:
                pass

    print(f"   IT_High 피봇: {len(it_high_pivots)}개")
    print(f"   IT_Low 피봇: {len(it_low_pivots)}개")

    # 각 데이터에 겹침 개수 추가
    for row in data:
        row['IT_High_Overlap'] = 0
        row['IT_Low_Overlap'] = 0

    # IT_High 겹침 계산
    for i, pivot in enumerate(it_high_pivots):
        overlap_count = 0
        price = pivot['price']
        atr = pivot['atr']

        # 겹침 범위 (ATR × multiplier)
        overlap_threshold = atr  # ATR은 이미 %로 계산되어 있음
        price_range_pct = overlap_threshold * overlap_range_atr_multiplier

        # 가격 범위
        price_high = price * (1 + price_range_pct / 100)
        price_low = price * (1 - price_range_pct / 100)

        # 다른 피봇들과 비교
        for j, other in enumerate(it_high_pivots):
            if i != j:  # 자기 자신 제외
                if price_low <= other['price'] <= price_high:
                    overlap_count += 1

        # 해당 인덱스에 겹침 개수 저장
        data[pivot['index']]['IT_High_Overlap'] = overlap_count

    # IT_Low 겹침 계산
    for i, pivot in enumerate(it_low_pivots):
        overlap_count = 0
        price = pivot['price']
        atr = pivot['atr']

        overlap_threshold = atr
        price_range_pct = overlap_threshold * overlap_range_atr_multiplier

        price_high = price * (1 + price_range_pct / 100)
        price_low = price * (1 - price_range_pct / 100)

        for j, other in enumerate(it_low_pivots):
            if i != j:
                if price_low <= other['price'] <= price_high:
                    overlap_count += 1

        data[pivot['index']]['IT_Low_Overlap'] = overlap_count

    # 현재 가장 가까운 피봇의 겹침 개수 전파
    print("\n   현재 캔들에 가장 가까운 피봇의 겹침 개수 전파 중...")

    last_high_overlap = 0
    last_low_overlap = 0

    for row in data:
        # IT_High 피봇이 있으면 업데이트
        if row['IT_High'] and row['IT_High'].strip():
            last_high_overlap = row['IT_High_Overlap']

        # IT_Low 피봇이 있으면 업데이트
        if row['IT_Low'] and row['IT_Low'].strip():
            last_low_overlap = row['IT_Low_Overlap']

        # 현재 캔들의 가장 가까운 피봇 겹침 개수 설정
        row['Closest_High_Overlap'] = last_high_overlap
        row['Closest_Low_Overlap'] = last_low_overlap

    # 저장
    output_path = csv_path.replace('.csv', '_with_overlap.csv')
    with open(output_path, 'w', newline='') as f:
        headers = list(data[0].keys())
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

    print(f"\n💾 저장 완료: {output_path}")

    # 통계
    high_overlaps = [p for p in it_high_pivots if data[p['index']]['IT_High_Overlap'] > 0]
    low_overlaps = [p for p in it_low_pivots if data[p['index']]['IT_Low_Overlap'] > 0]

    print(f"\n📊 겹침 통계:")
    print(f"   IT_High 피봇 중 겹침 있음: {len(high_overlaps)}개")
    print(f"   IT_Low 피봇 중 겹침 있음: {len(low_overlaps)}개")

    # 겹침 많은 피봇 예시
    print(f"\n🔥 겹침이 많은 IT_High 피봇 (Top 5):")
    sorted_high = sorted(it_high_pivots,
                        key=lambda x: data[x['index']]['IT_High_Overlap'],
                        reverse=True)[:5]
    for p in sorted_high:
        overlap = data[p['index']]['IT_High_Overlap']
        if overlap > 0:
            print(f"   {p['time']}: {p['price']:.2f} (겹침: {overlap}개)")

    print(f"\n🔥 겹침이 많은 IT_Low 피봇 (Top 5):")
    sorted_low = sorted(it_low_pivots,
                       key=lambda x: data[x['index']]['IT_Low_Overlap'],
                       reverse=True)[:5]
    for p in sorted_low:
        overlap = data[p['index']]['IT_Low_Overlap']
        if overlap > 0:
            print(f"   {p['time']}: {p['price']:.2f} (겹침: {overlap}개)")

    return data, output_path

if __name__ == "__main__":
    csv_file = 'BITGET_BTCUSDT.P, 60_7fbcf.csv'

    print("🚀 피봇 겹침 개수 계산 시작...\n")

    data, output_file = calculate_pivot_overlap(csv_file, overlap_range_atr_multiplier=1.0)

    print(f"\n\n✅ 완료! 새 파일을 사용하세요: {output_file}")
